import os
import supervisely_lib as sly
from supervisely_lib.aug.aug import resize
# ----------------------------------------------------------------------------------------------------------------------
# ------------- init app and api ---------------------------------------------------------------------------------------
api: sly.Api = sly.Api.from_env()
app: sly.AppService = sly.AppService()
# ----------------------------------------------------------------------------------------------------------------------
# -------------- get additional data -----------------------------------------------------------------------------------
team_id      = int(os.environ['context.teamId'])            # from debug.env
workspace_id = int(os.environ['context.workspaceId'])       # from debug.env
project_id   = int(os.environ['modal.state.slyProjectId'])  # from debug.env
task_id      = int(os.environ["TASK_ID"])                   # from debug.env
new_project_name = os.environ["modal.state.projectName"]    # from debug.env
# ----------------------------------------------------------------------------------------------------------------------
# -------------- init global variables ---------------------------------------------------------------------------------
global TARGET_HEIGHT, TARGET_WIDTH
TARGET_HEIGHT = int(os.environ["modal.state.targetHeight"]) # TARGET_HEIGHT need to be defined
TARGET_WIDTH  = int(os.environ["modal.state.targetWidth"])  # TARGET_WIDTH need to be defined
# check for target params
assert TARGET_HEIGHT is not None or TARGET_WIDTH is not None, "Target shape is not defined!..."
target_height = TARGET_HEIGHT if TARGET_HEIGHT is not None else -1
target_width  = TARGET_WIDTH  if TARGET_WIDTH  is not None else -1
# ----------------------------------------------------------------------------------------------------------------------
# -------------- init global variables ---------------------------------------------------------------------------------
# SRC - source
# DST - destination
# Get SRC project info and create DST project for transformed(resized) data
src_project = app.public_api.project.get_info_by_id(project_id)
if src_project is None:
    raise RuntimeError(f"Project id={project_id} not found")

if new_project_name == 'default' or new_project_name is None:
    new_project_name = src_project.name + '_resized'
dst_project = api.project.create(workspace_id, new_project_name, change_name_if_conflict=True)
app.logger.info("Result Project is created (name={!r}; id={})".format(dst_project.name, dst_project.id))
# ----------------------------------------------------------------------------------------------------------------------
# -------------- get meta-info from src_project and copy to dst_project ------------------------------------------------
meta = sly.ProjectMeta.from_json(app.public_api.project.get_meta(project_id))
if len(meta.obj_classes) == 0:
    raise ValueError("Project should have at least one class")
api.project.update_meta(dst_project.id, meta.to_json())
# ----------------------------------------------------------------------------------------------------------------------
# -------------- process each dataset for each project and dump results to new project ---------------------------------
# logger initialisation
progress = sly.Progress("Processing", src_project.images_count, ext_logger=app.logger)
# dataset_level
for dataset in api.dataset.get_list(src_project.id):
    destination_dataset = api.dataset.create(dst_project.id, dataset.name)
    ds_images = api.image.get_list(dataset.id)
    # batch_level (data will be downloaded/uploaded as batches(N images and annotation_data) to improve time management)
    for batch in sly.batched(ds_images, batch_size = 10):
        image_ids   = [image_info.id   for image_info in batch]     # image indexes in batch
        image_names = [image_info.name for image_info in batch]     # image names in batch
        image_metas = [image_info.meta for image_info in batch]     # image metas in batch
        image_nps   = api.image.download_nps(dataset.id, image_ids) # images <np.ndarrray>s

        ann_infos = api.annotation.download_batch(dataset.id, image_ids)
        anns      = [sly.Annotation.from_json(ann_info.annotation, meta) for ann_info in ann_infos]

        destination_ids         = []
        destination_image_names = []
        destination_metas       = []
        resized_images_nps      = []
        resized_annotations     = []
        for image_id, image_name, image_np, image_meta, annotation in zip(image_ids, image_names, image_nps, image_metas, anns):
            destination_ids.append(image_id)
            destination_image_names.append(image_name)
            destination_metas.append(image_meta)
            # data transformation stage
            resized_image_np, resized_annotation = resize(image_np, annotation, size = (target_height, target_width))
            resized_images_nps.append(resized_image_np)
            resized_annotations.append(resized_annotation)
        # upload transformed 'np.ndarray's and annotations to dst_project dataset
        resized_images_info = api.image.upload_nps(dataset_id = destination_dataset.id,
                                                   names      = destination_image_names,
                                                   imgs       = resized_images_nps)

        resized_images_ids = [image_info.id for image_info in resized_images_info]
        api.annotation.upload_anns(resized_images_ids, resized_annotations)
        progress.iters_done_report(len(resized_images_ids))
