from collections import Counter
from typing import Tuple

import pandas as pd
import supervisely as sly
from supervisely.app.widgets import (
    Button,
    Card,
    Checkbox,
    ClassicTable,
    Container,
    Empty,
    Field,
    Flexbox,
    Input,
    InputNumber,
    OneOf,
    Progress,
    ProjectThumbnail,
    Switch,
    Text,
)
from supervisely.aug.aug import resize

import src.globals as g

src_project_info = g.api.project.get_info_by_id(g.PROJECT_ID)
src_project_thumbnail = ProjectThumbnail(src_project_info)
src_project_card = Card(
    title="1️⃣ Source Project",
    description="All images from this project will be resized",
    content=src_project_thumbnail,
)

sizes_dict = {}
for dataset in g.api.dataset.get_list(g.PROJECT_ID):
    for image in g.api.image.get_list(dataset.id):
        sizes_dict[image.id] = (image.width, image.height)

size_counts = Counter(sizes_dict.values())
sorted_sizes = sorted(size_counts.items(), key=lambda x: x[1], reverse=True)
most_frequent_sizes = [
    (count, round(100 * count / len(sizes_dict), 1), size)
    for size, count in sorted_sizes[:10]
]


sizes_frequencies_table = ClassicTable()
sizes_frequencies_table.read_pandas(
    pd.DataFrame(data=most_frequent_sizes, columns=["Count", "Count (%)", "Size"])
)

sizes_frequencies_table_card = Card(
    title="2️⃣ Most frequent image sizes [ width x height ]",
    description="Discover images sizes statistics",
    content=sizes_frequencies_table,
)

input_width = InputNumber(most_frequent_sizes[0][2][0])
input_height = InputNumber(most_frequent_sizes[0][2][1])
input_width_percent = InputNumber(min=1, value=100)
input_height_percent = InputNumber(min=1, value=100)
auto_width_checkbox = Checkbox("")
width_checkbox_and_text = Flexbox(
    widgets=[
        auto_width_checkbox,
        Text(
            '<div style="display:flex; flex-direction: column;"><b>auto width</b><span style="color: #7f858e;">adjust width proportionally (keep aspect ratio)</span></div>'
        ),
    ],
    gap=0,
)
auto_height_checkbox = Checkbox("")
height_checkbox_and_text = Flexbox(
    widgets=[
        auto_height_checkbox,
        Text(
            '<div style="display:flex; flex-direction: column;"><b>auto height</b><span style="color: #7f858e;">adjust height proportionally (keep aspect ratio)</span></div>'
        ),
    ],
    gap=0,
)
width_switch = Switch(
    on_text="px",
    off_text="%",
    off_color="#20a0ff",
    on_content=input_width,
    off_content=input_width_percent,
    switched=True,
)
height_switch = Switch(
    on_text="px",
    off_text="%",
    off_color="#20a0ff",
    on_content=input_height,
    off_content=input_height_percent,
    switched=True,
)
width_row = Flexbox(
    widgets=[
        Container(widgets=[Empty(), Text("<b>Width:</b>")], gap=7),
        Flexbox(widgets=[OneOf(width_switch), width_switch, width_checkbox_and_text]),
    ],
    gap=14,
)
height_row = Flexbox(
    widgets=[
        Container(widgets=[Empty(), Text("<b>Height:</b>")], gap=7),
        Flexbox(widgets=[OneOf(height_switch), height_switch, height_checkbox_and_text]),
    ],
    gap=10,
)


@auto_height_checkbox.value_changed
def auto_height_checkbox_changed(value):
    if value:
        # if auto height
        # disable height inputs
        input_height.disable()
        input_height_percent.disable()
        height_switch.disable()
        # uncheck auto width and enable width inputs
        auto_width_checkbox.uncheck()
        input_width.enable()
        input_width_percent.enable()
        width_switch.enable()
    else:
        # if not auto height
        # enable height inputs
        input_height.enable()
        input_height_percent.enable()
        height_switch.enable()


@auto_width_checkbox.value_changed
def auto_width_checkbox_changed(value):
    if value:
        # if auto width
        # disable width inputs
        input_width.disable()
        input_width_percent.disable()
        width_switch.disable()
        # if not auto height
        # uncheck auto height and enable height inputs
        auto_height_checkbox.uncheck()
        input_height.enable()
        input_height_percent.enable()
        height_switch.enable()
    else:
        # if not auto width
        # enable width inputs
        input_width.enable()
        input_width_percent.enable()
        width_switch.enable()


input_newsize = Container([Empty(), width_row, height_row])
newsize_card = Card(
    title="3️⃣ Specify new size",
    description="Input new sizes in pixels or percents",
    content=input_newsize,
)

input_newproject = Input(placeholder="Resized project name")

container_newproject = Container([input_newproject, Empty()], "horizontal", fractions=[22, 36])
newproject_card = Card(
    title="4️⃣ New project name",
    description="Resized images will be saved to a new project with the following name",
    content=container_newproject,
)

button_run = Button("Run")
progress_bar = Progress(show_percents=False)
dst_project_thumbnail = ProjectThumbnail()
dst_project_card = Card(title="✅ Destination project", content=dst_project_thumbnail)
notification = Text()

hideables = Container(
    widgets=[
        dst_project_card,
        progress_bar,
        notification,
    ],
    gap=0,
)

layout = Container(
    widgets=[
        src_project_card,
        sizes_frequencies_table_card,
        newsize_card,
        newproject_card,
        button_run,
        hideables,
    ],
    gap=20,
)


notification.hide()
dst_project_card.hide()
progress_bar.hide()


def get_width() -> Tuple[int, bool, bool]:
    is_auto = auto_width_checkbox.is_checked()
    if width_switch.is_switched():
        return input_width.get_value(), True, is_auto
    else:
        return input_width_percent.get_value(), False, is_auto


def get_height() -> Tuple[int, bool, bool]:
    is_auto = auto_height_checkbox.is_checked()
    if height_switch.is_switched():
        return input_height.get_value(), True, is_auto
    else:
        return input_height_percent.get_value(), False, is_auto


def get_target_size(
    source_size: Tuple[int, int],
    target_width_value,
    is_width_px,
    auto_width,
    target_height_value,
    is_height_px,
    auto_height,
):
    width = source_size[0]
    height = source_size[1]
    if auto_width:
        height = (
            target_height_value if is_height_px else (target_height_value * source_size[1]) / 100
        )
        width = (height * source_size[0]) / source_size[1]
    elif auto_height:
        width = target_width_value if is_width_px else (target_width_value * source_size[0]) / 100
        height = (width * source_size[1]) / source_size[0]
    else:
        width = target_width_value if is_width_px else (target_width_value * source_size[0]) / 100
        height = (
            target_height_value if is_height_px else (target_height_value * source_size[1]) / 100
        )
    return (int(width), int(height))


@button_run.click
def resize_images():
    notification.hide()
    dst_project_card.hide()
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

    target_width_value, is_width_px, auto_width = get_width()
    target_height_value, is_height_px, auto_height = get_height()

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
                target_sizes = [
                    get_target_size(
                        source_size=(image_info.width, image_info.height),
                        target_width_value=target_width_value,
                        is_width_px=is_width_px,
                        auto_width=auto_width,
                        target_height_value=target_height_value,
                        is_height_px=is_height_px,
                        auto_height=auto_height,
                    )
                    for image_info in batch
                ]

                ann_infos = g.api.annotation.download_batch(dataset.id, image_ids)
                anns = [
                    sly.Annotation.from_json(ann_info.annotation, meta) for ann_info in ann_infos
                ]

                destination_ids = []
                destination_image_names = []
                resized_images_nps = []
                resized_annotations = []
                for (
                    image_id,
                    image_name,
                    image_np,
                    image_meta,
                    annotation,
                    target_size,
                ) in zip(image_ids, image_names, image_nps, image_metas, anns, target_sizes):
                    try:
                        # data transformation stage
                        resized_image_np, resized_annotation = resize(
                            image_np, annotation, size=(target_size[1], target_size[0])
                        )
                    except ValueError as exc:
                        sly.logger.warn(f"Error while resizing image {image_name} with id={image_id}, skiping...")
                        pbar.update(1)
                        continue
                    destination_ids.append(image_id)
                    destination_image_names.append(image_name)
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
    dst_project_thumbnail.set(project_info)
    dst_project_card.show()
