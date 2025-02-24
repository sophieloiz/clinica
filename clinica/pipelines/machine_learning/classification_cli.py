from typing import Optional

import click

from clinica import option
from clinica.pipelines import cli_param
from clinica.pipelines.engine import clinica_pipeline
from clinica.utils.atlas import T1_VOLUME_ATLASES

pipeline_name = "machinelearning-classification"


@clinica_pipeline
@click.command(name=pipeline_name)
@cli_param.argument.caps_directory
@cli_param.argument.group_label
@click.argument(
    "orig_input_data",
    type=click.Choice(["VoxelBased", "RegionBased"]),
)
@click.argument(
    "image_type",
    type=click.Choice(["T1w", "PET"]),
)
@click.argument(
    "algorithm",
    type=click.Choice(["DualSVM", "LogisticRegression", "RandomForest"]),
)
@click.argument(
    "validation",
    type=click.Choice(["RepeatedHoldOut", "RepeatedKFoldCV"]),
)
@click.argument(
    "subjects_visits_tsv",
    type=click.Path(exists=True, resolve_path=True),
)
@click.argument(
    "diagnoses_tsv",
    type=click.Path(exists=True, resolve_path=True),
)
@click.argument(
    "output_directory", type=click.Path(exists=False, writable=True, resolve_path=True)
)
@cli_param.option_group.pipeline_specific_options
@cli_param.option.acq_label
@cli_param.option.suvr_reference_region
@cli_param.option_group.option(
    "-atlas",
    "--atlas",
    type=click.Choice(T1_VOLUME_ATLASES),
    help="One of the atlases generated by t1-volume or pet-volume pipeline.",
)
@cli_param.option_group.common_pipelines_options
@option.global_option_group
@option.n_procs
def cli(
    caps_directory: str,
    group_label: str,
    orig_input_data: str,
    image_type: str,
    algorithm: str,
    validation: str,
    subjects_visits_tsv: str,
    diagnoses_tsv: str,
    output_directory: str,
    acq_label: Optional[str] = None,
    suvr_reference_region: Optional[str] = None,
    atlas: Optional[str] = None,
    n_procs: Optional[int] = None,
) -> None:
    """Classification based on machine learning using scikit-learn.


        GROUP_LABEL is a string defining the group label for the current analysis, which helps you keep track of different analyses.

        The third positional argument defines the type of features for classification. It can be 'RegionBased' or 'VoxelBased'.

        The fourth positional argument defines the studied modality ('T1w' or 'PET')

        The fifth positional argument defines the algorithm. It can be 'DualSVM', 'LogisticRegression' or 'RandomForest'.

        The sixth positional argument defines the validation method. It can be 'RepeatedHoldOut' or 'RepeatedKFoldCV'.

        SUBJECTS_VISITS_TSV is a TSV file containing the participant_id and the session_id columns

        DIAGNOSES_TSV is a TSV file where the diagnosis for each participant (identified by a participant ID) is reported (e.g. AD, CN). It allows the algorithm to perform the dual classification (between the two labels reported).

    See https://aramislab.paris.inria.fr/clinica/docs/public/latest/Pipelines/MachineLearning_Classification/
    """
    from clinica.utils.exceptions import ClinicaException

    from .ml_workflows import (
        RegionBasedRepHoldOutDualSVM,
        RegionBasedRepHoldOutLogisticRegression,
        RegionBasedRepHoldOutRandomForest,
        RegionBasedRepKFoldDualSVM,
        VoxelBasedRepHoldOutDualSVM,
        VoxelBasedRepKFoldDualSVM,
    )

    if image_type == "PET":
        if not acq_label:
            raise ClinicaException(
                "You selected PET inputs without setting --acq_label flag. "
                "Clinica will now exit."
            )
        if not suvr_reference_region:
            raise ClinicaException(
                "You selected PET inputs without setting --suvr_reference_region flag. "
                "Clinica will now exit."
            )

    if orig_input_data == "RegionBased" and not atlas:
        raise ClinicaException(
            "You selected region-based inputs without setting --atlas flag. "
            "Clinica will now exit."
        )

    if algorithm in ["LogisticRegression", "RandomForest"]:
        if orig_input_data != "RegionBased" or validation != "RepeatedHoldOut":
            raise ClinicaException(
                "LogisticRegression or RandomForest algorithm can only work on region-based featured or RepeatedHoldOut algorithm. "
                "Clinica will now exit."
            )

    if (
        (orig_input_data == "RegionBased")
        and (validation == "RepeatedHoldOut")
        and (algorithm == "DualSVM")
    ):
        pipeline = RegionBasedRepHoldOutDualSVM(
            caps_directory=caps_directory,
            subjects_visits_tsv=subjects_visits_tsv,
            diagnoses_tsv=diagnoses_tsv,
            group_label=group_label,
            image_type=image_type,
            output_dir=output_directory,
            acq_label=acq_label,
            suvr_reference_region=suvr_reference_region,
            atlas=atlas,
            n_threads=n_procs,
        )
    elif (
        (orig_input_data == "RegionBased")
        and (validation == "RepeatedKFoldCV")
        and (algorithm == "DualSVM")
    ):
        pipeline = RegionBasedRepKFoldDualSVM(
            caps_directory=caps_directory,
            subjects_visits_tsv=subjects_visits_tsv,
            diagnoses_tsv=diagnoses_tsv,
            group_label=group_label,
            image_type=image_type,
            output_dir=output_directory,
            acq_label=acq_label,
            suvr_reference_region=suvr_reference_region,
            atlas=atlas,
            n_threads=n_procs,
        )
    elif (
        (orig_input_data == "RegionBased")
        and (validation == "RepeatedHoldOut")
        and (algorithm == "LogisticRegression")
    ):
        pipeline = RegionBasedRepHoldOutLogisticRegression(
            caps_directory=caps_directory,
            subjects_visits_tsv=subjects_visits_tsv,
            diagnoses_tsv=diagnoses_tsv,
            group_label=group_label,
            image_type=image_type,
            output_dir=output_directory,
            acq_label=acq_label,
            suvr_reference_region=suvr_reference_region,
            atlas=atlas,
            n_threads=n_procs,
        )
    elif (
        (orig_input_data == "RegionBased")
        and (validation == "RepeatedHoldOut")
        and (algorithm == "RandomForest")
    ):
        pipeline = RegionBasedRepHoldOutRandomForest(
            caps_directory=caps_directory,
            subjects_visits_tsv=subjects_visits_tsv,
            diagnoses_tsv=diagnoses_tsv,
            group_label=group_label,
            image_type=image_type,
            output_dir=output_directory,
            acq_label=acq_label,
            suvr_reference_region=suvr_reference_region,
            atlas=atlas,
            n_threads=n_procs,
        )
    elif (
        (orig_input_data == "VoxelBased")
        and (validation == "RepeatedHoldOut")
        and (algorithm == "DualSVM")
    ):
        pipeline = VoxelBasedRepHoldOutDualSVM(
            caps_directory=caps_directory,
            subjects_visits_tsv=subjects_visits_tsv,
            diagnoses_tsv=diagnoses_tsv,
            group_label=group_label,
            image_type=image_type,
            output_dir=output_directory,
            acq_label=acq_label,
            suvr_reference_region=suvr_reference_region,
            n_threads=n_procs,
        )
    elif (
        (orig_input_data == "VoxelBased")
        and (validation == "RepeatedKFoldCV")
        and (algorithm == "DualSVM")
    ):
        pipeline = VoxelBasedRepKFoldDualSVM(
            caps_directory=caps_directory,
            subjects_visits_tsv=subjects_visits_tsv,
            diagnoses_tsv=diagnoses_tsv,
            group_label=group_label,
            image_type=image_type,
            output_dir=output_directory,
            acq_label=acq_label,
            suvr_reference_region=suvr_reference_region,
            n_threads=n_procs,
        )
    else:
        raise ClinicaException(
            "Unknown combination of machine learning classification."
        )

    pipeline.run()


if __name__ == "__main__":
    cli()
