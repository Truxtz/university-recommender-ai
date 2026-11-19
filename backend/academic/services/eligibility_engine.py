
from ..models import (
    Combination,
    CombinationSubject,
    GradeScale,
    ProgrammeEligibilityRule,
)


def evaluate_eligibility(combination_code, grades):
    """
    Evaluate student eligibility against programme
    requirements stored in the database.

    Principal subject pass: D or better.
    Subsidiary subject pass: S or better.

    Mathematics (M) is compulsory for ALL specialist
    and BEd programmes in PCM, PGM and EGM.
    """

    try:
        combination = Combination.objects.get(
            code=combination_code
        )
    except Combination.DoesNotExist:
        return {
            "eligible_programmes": [],
            "total_points": 0,
            "failed_principal_subjects": [],
            "all_principal_subjects_failed": False,
            "maths_subject_code": None,
            "maths_passed": True,
        }

    grade_scales = {
        item.grade: item
        for item in GradeScale.objects.all()
    }

    principal_pass_points = grade_scales["D"].points
    subsidiary_pass_points = grade_scales["S"].points

    combination_subjects = list(
        CombinationSubject.objects
        .filter(combination=combination)
        .select_related("subject")
    )

    principal_subjects = [
        item.subject.code
        for item in combination_subjects
        if item.is_principal
    ]

    total_points = 0
    failed_principal_subjects = []

    for subject_code in principal_subjects:
        grade = grades.get(subject_code)
        grade_scale = grade_scales.get(grade)

        if not grade_scale:
            return {
                "eligible_programmes": [],
                "total_points": 0,
                "failed_principal_subjects": [],
                "all_principal_subjects_failed": False,
                "maths_subject_code": None,
                "maths_passed": False,
            }

        total_points += grade_scale.points

        if grade_scale.points < principal_pass_points:
            failed_principal_subjects.append(subject_code)

    # Identify the mathematics subject for the combination
    maths_subject_code = None

    for item in combination_subjects:
        if item.subject.code in ["BAM", "M"]:
            maths_subject_code = item.subject.code
            break

    # Evaluate mathematics pass requirement
    maths_passed = True

    if maths_subject_code:
        maths_grade = grades.get(maths_subject_code)
        maths_scale = grade_scales.get(maths_grade)

        if maths_subject_code == "BAM":
            maths_passed = (
                maths_scale is not None
                and maths_scale.points >= subsidiary_pass_points
            )

        elif maths_subject_code == "M":
            maths_passed = (
                maths_scale is not None
                and maths_scale.points >= principal_pass_points
            )

    rules = (
        ProgrammeEligibilityRule.objects
        .filter(combination=combination)
        .select_related(
            "degree_programme",
            "maths_subject",
        )
        .prefetch_related(
            "subject_requirements__subject",
            "subject_requirements__minimum_grade",
        )
    )

    eligible_programmes = []

    for rule in rules:
        eligible = True

        # Check minimum principal subject points
        if total_points < rule.minimum_points:
            eligible = False

        # Check compulsory mathematics requirement
        if rule.maths_subject:
            maths_code = rule.maths_subject.code

            if maths_code == "BAM" and not maths_passed:
                eligible = False

            elif maths_code == "M" and not maths_passed:
                # Failed Advanced Mathematics excludes
                # ALL specialist and BEd programmes
                # in PCM, PGM and EGM.
                eligible = False

        # Check individual programme subject requirements
        for requirement in rule.subject_requirements.all():
            subject_code = requirement.subject.code
            student_grade = grades.get(subject_code)
            student_scale = grade_scales.get(student_grade)

            minimum_points = requirement.minimum_grade.points

            if (
                not student_scale
                or student_scale.points < minimum_points
            ):
                eligible = False
                break

        if eligible:
            eligible_programmes.append({
                "degree": rule.degree_programme.name,
                "rule_id": rule.id,
            })

    all_principal_subjects_failed = (
        bool(principal_subjects)
        and len(failed_principal_subjects)
        == len(principal_subjects)
    )

    return {
        "eligible_programmes": eligible_programmes,
        "total_points": total_points,
        "failed_principal_subjects": failed_principal_subjects,
        "all_principal_subjects_failed": all_principal_subjects_failed,
        "maths_subject_code": maths_subject_code,
        "maths_passed": maths_passed,
    }
