from collections import Counter

import pandas as pd
import supervisely as sly
from supervisely.app.widgets import (
    BindedInputNumber,
    Button,
    Card,
    ClassicTable,
    Container,
    Empty,
    Field,
    Input,
    Progress,
    ProjectThumbnail,
    Text,
)
from supervisely.aug.aug import resize

import src.globals as g

project_info = g.api.project.get_info_by_id(g.PROJECT_ID)

sizes_dict = {}
for dataset in g.api.dataset.get_list(g.PROJECT_ID):
    for image in g.api.image.get_list(dataset.id):
        sizes_dict[image.id] = (image.width, image.height)

size_counts = Counter(sizes_dict.values())
sorted_sizes = sorted(size_counts.items(), key=lambda x: x[1], reverse=True)
most_frequent_sizes = [(count, size) for size, count in sorted_sizes[:10]]


classic_table = ClassicTable()
classic_table.read_pandas(pd.DataFrame(data=most_frequent_sizes, columns=["Count", "Size"]))

field_table = Field(classic_table, "Most frequent image sizes [ width x height ]")

input_newsize = BindedInputNumber(
    width=most_frequent_sizes[0][1][0], height=most_frequent_sizes[0][1][1], proportional=True
)
field_newsize = Field(input_newsize, "Specify new size")

input_newproject = Input(placeholder="Input new project name")

container_newproject = Container([input_newproject, Empty()], "horizontal", fractions=[3, 8])

button_resize = Button("Resize")
progress_bar = Progress(show_percents=False)
project_thumbnail = ProjectThumbnail()
notification = Text()


card_1 = Card(
    title=f"Resize all images in '{project_info.name}' project",
    content=Container(
        widgets=[
            field_table,
            field_newsize,
            container_newproject,
            button_resize,
            progress_bar,
            notification,
            project_thumbnail,
        ]
    ),
)


notification.hide()
project_thumbnail.hide()
progress_bar.hide()


@button_resize.click
def resize_images():
    notification.hide()
    project_thumbnail.hide()
    progress_bar.hide()

    new_project_name = input_newproject.get_value()
    if new_project_name == "":
        notification.text = "Please enter a new project name"
        notification.status = "warning"
        notification.show()
        return

    src_project = g.api.project.get_info_by_id(g.PROJECT_ID)
    if src_project is None:
        notification.text = f"Project id={g.PROJECT_ID} not found"
        notification.status = "error"
        notification.show()
        return

    dst_project = g.api.project.create(
        g.WORKSPACE_ID, new_project_name, change_name_if_conflict=True
    )

    target_width, target_height = input_newsize.get_value()

    meta = sly.ProjectMeta.from_json(g.api.project.get_meta(g.PROJECT_ID))
    g.api.project.update_meta(dst_project.id, meta.to_json())

    progress_bar.show()

    with progress_bar(message="Processing", total=src_project.images_count) as pbar:
        for dataset in g.api.dataset.get_list(src_project.id):
            destination_dataset = g.api.dataset.create(dst_project.id, dataset.name)
            ds_images = g.api.image.get_list(dataset.id)
            # batch_level (data will be downloaded/uploaded as batches(N images and annotation_data)
            # to improve time management)
            for batch in sly.batched(ds_images, batch_size=10):
                image_ids = [image_info.id for image_info in batch]  # image indexes in batch
                image_names = [image_info.name for image_info in batch]  # image names in batch
                image_metas = [image_info.meta for image_info in batch]  # image metas in batch
                image_nps = g.api.image.download_nps(dataset.id, image_ids)  # images <np.ndarrray>s

                ann_infos = g.api.annotation.download_batch(dataset.id, image_ids)
                anns = [
                    sly.Annotation.from_json(ann_info.annotation, meta) for ann_info in ann_infos
                ]

                destination_ids = []
                destination_image_names = []
                resized_images_nps = []
                resized_annotations = []
                for image_id, image_name, image_np, image_meta, annotation in zip(
                    image_ids, image_names, image_nps, image_metas, anns
                ):
                    destination_ids.append(image_id)
                    destination_image_names.append(image_name)
                    # data transformation stage
                    resized_image_np, resized_annotation = resize(
                        image_np, annotation, size=(target_height, target_width)
                    )
                    resized_images_nps.append(resized_image_np)
                    resized_annotations.append(resized_annotation)
                # upload transformed 'np.ndarray's and annotations to dst_project dataset
                resized_images_info = g.api.image.upload_nps(
                    dataset_id=destination_dataset.id,
                    names=destination_image_names,
                    imgs=resized_images_nps,
                )

                resized_images_ids = [image_info.id for image_info in resized_images_info]
                g.api.annotation.upload_anns(resized_images_ids, resized_annotations)
                # progress.iters_done_report(len(resized_images_ids))
                pbar.update(len(resized_images_ids))

    project_info = g.api.project.get_info_by_id(dst_project.id)
    project_thumbnail.set(project_info)
    project_thumbnail.show()
