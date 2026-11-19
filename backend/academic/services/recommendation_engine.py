
from ..models import (
    ProgrammeEligibilityRule,
    ProgrammeSubjectRequirement,
    GradeScale,
)


def calculate_academic_match(grades, eligible_programmes):
    """
    Calculate academic match percentages for eligible programmes.

    The eligibility engine determines qualification.
    This engine only calculates and ranks academic matches.

    Formula:
    Student points in required subjects /
    Maximum possible points in required subjects * 100
    """

    grade_scales = {
        item.grade: item
        for item in GradeScale.objects.all()
    }

    maximum_grade_points = max(
        float(item.points)
        for item in grade_scales.values()
    )

    recommendations = []

    for programme in eligible_programmes:

        rule = ProgrammeEligibilityRule.objects.get(
            id=programme["rule_id"]
        )

        requirements = (
            ProgrammeSubjectRequirement.objects
            .filter(eligibility_rule=rule)
            .select_related("subject")
        )

        student_points = 0
        maximum_points = 0

        for requirement in requirements:

            subject_code = requirement.subject.code
            student_grade = grades.get(subject_code)
            grade_scale = grade_scales.get(student_grade)

            if not grade_scale:
                continue

            student_points += float(grade_scale.points)
            maximum_points += maximum_grade_points

        if maximum_points == 0:
            continue

        academic_match = (
            student_points / maximum_points
        ) * 100

        recommendations.append({
            "degree": programme["degree"],
            "rule_id": programme["rule_id"],
            "suitability_score": round(academic_match, 2),
        })

    recommendations.sort(
        key=lambda item: item["suitability_score"],
        reverse=True
    )

    return recommendations
