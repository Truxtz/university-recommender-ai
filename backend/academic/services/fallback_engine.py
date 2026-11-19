
from ..models import (
    ProgrammeEligibilityRule,
    CombinationSubject,
)


def recommend_fallback(eligibility_result, combination_code):
    """
    Recommend an alternative academic pathway when
    no available degree programme is suitable.
    """

    eligible_programmes = eligibility_result.get(
        "eligible_programmes", []
    )

    if eligible_programmes:
        return None

    all_principal_failed = eligibility_result.get(
        "all_principal_subjects_failed", False
    )

    failed_principal_subjects = eligibility_result.get(
        "failed_principal_subjects", []
    )

    maths_subject_code = eligibility_result.get(
        "maths_subject_code"
    )

    maths_passed = eligibility_result.get(
        "maths_passed", True
    )

    # Retrieve the student's principal subjects
    principal_subjects = (
        CombinationSubject.objects
        .filter(
            combination__code=combination_code,
            is_principal=True,
        )
        .select_related("subject")
    )

    principal_names = [
        item.subject.name
        for item in principal_subjects
    ]

    # All three principal subjects failed
    if all_principal_failed:
        return {
            "category": "DIPLOMA",
            "title": "Explore Diploma Programmes",
            "message": (
                "Your results do not meet the minimum "
                "principal-subject pass requirements for "
                "the available degree programmes. "
                "Consider exploring Diploma programmes "
                "as an alternative academic pathway."
            ),
            "reason": (
                "All three principal subjects are below "
                "the required passing grade of D."
            ),
        }

    # Mathematics requirement failed
    if maths_subject_code and not maths_passed:

        restricted_rules = (
            ProgrammeEligibilityRule.objects
            .filter(
                combination__code=combination_code,
                maths_subject__code=maths_subject_code,
            )
            .select_related("degree_programme")
        )

        specialist_programmes = []
        education_programmes = []

        for rule in restricted_rules:
            programme_name = rule.degree_programme.name

            is_bed = programme_name.startswith(
                "Bachelor of Education in "
            )

            if is_bed:
                teaching_subject = programme_name.replace(
                    "Bachelor of Education in ", "", 1
                )

                if teaching_subject in principal_names:
                    education_programmes.append(programme_name)

            else:
                specialist_programmes.append(programme_name)

        specialist_text = ", ".join(
            specialist_programmes
        )

        education_text = ", ".join(
            education_programmes
        )

        if maths_subject_code == "BAM":
            maths_name = "Basic Applied Mathematics (BAM)"
        else:
            maths_name = "Advanced Mathematics (Pure Mathematics)"

        message = (
            f"Because you did not pass {maths_name}, "
            "you are not eligible for the applicable "
            "specialist degree programmes"
        )

        if specialist_text:
            message += f", such as {specialist_text}"

        if education_text:
            message += (
                ", or the Bachelor of Education programmes "
                f"corresponding to your principal subjects, "
                f"such as {education_text}"
            )

        message += (
            ". Therefore, consider exploring degree "
            "programmes in Social Sciences and Humanities. "
            "Check the specific admission requirements "
            "of the respective universities."
        )

        return {
            "category": "ALTERNATIVE_DEGREE",
            "title": "Explore Social Sciences and Humanities",
            "message": message,
            "reason": (
                f"{maths_name} is a compulsory requirement "
                "for the listed programmes, and your grade "
                "does not meet its passing threshold."
            ),
        }

    # One or two principal subjects failed
    if failed_principal_subjects:
        reason = (
            "Although some principal subjects are below "
            "grade D, you have passed other principal "
            "subjects."
        )

    else:
        reason = (
            "You have passed your principal subjects but "
            "do not qualify for the degree programmes "
            "currently available in the system."
        )

    return {
        "category": "ALTERNATIVE_DEGREE",
        "title": "Explore Social Sciences and Humanities",
        "message": (
            "Consider exploring degree programmes in "
            "Social Sciences and Humanities. These are "
            "alternative academic areas to investigate; "
            "specific admission requirements should be "
            "checked with the respective universities."
        ),
        "reason": reason,
    }
