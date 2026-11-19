
from django.shortcuts import render, redirect

from .models import (
    Combination,
    CombinationSubject,
    GradeScale,
)

from .services.eligibility_engine import evaluate_eligibility
from .services.recommendation_engine import calculate_academic_match
from .services.fallback_engine import recommend_fallback


def home(request):

    combinations = {}

    all_combinations = (
        Combination.objects
        .prefetch_related("combination_subjects__subject")
        .all()
    )

    for combination in all_combinations:

        combinations[combination.code] = [
            {
                "code": item.subject.code,
                "name": item.subject.name,
            }
            for item in combination.combination_subjects.all()
        ]

    return render(request, "academic/index.html", {
        "combinations": combinations,
    })


def recommendations(request):

    if request.method != "POST":
        return redirect("home")

    combination_code = request.POST.get("combination")

    try:
        combination = Combination.objects.get(
            code=combination_code
        )
    except (Combination.DoesNotExist, TypeError, ValueError):
        return redirect("home")

    # 1. Retrieve the combination subjects.

    combination_subjects = (
        CombinationSubject.objects
        .filter(combination=combination)
        .select_related("subject")
    )

    # 2. Collect student grades.

    grades = {}
    display_grades = {}

    for item in combination_subjects:

        code = item.subject.code
        name = item.subject.name

        grade = request.POST.get(f"grade_{code}")

        grades[code] = grade
        display_grades[name] = grade

    # 3. Validate that every subject has a recognised grade.

    valid_grade_codes = set(
        GradeScale.objects.values_list("grade", flat=True)
    )

    if any(
        grades.get(item.subject.code) not in valid_grade_codes
        for item in combination_subjects
    ):
        return redirect("home")

    # 4. Evaluate degree programme eligibility.

    eligibility_result = evaluate_eligibility(
        combination.code,
        grades,
    )

    eligible_programmes = eligibility_result[
        "eligible_programmes"
    ]

    # 5. Preserve specialist programme display priorities.

    programme_priority = {
        "PCB": [
            "Doctor of Medicine (MD)",
            "Bachelor of Nursing",
            "Bachelor of Pharmacy",
        ],
        "CBG": [
            "Bachelor of Nursing",
            "Bachelor of Pharmacy",
        ],
        "PCM": [
            "Bachelor of Petroleum Engineering",
            "Bachelor of Aeronautical Engineering",
            "Bachelor of Telecommunications Engineering",
        ],
        "PGM": [
            "Bachelor of Petroleum Engineering",
            "Bachelor of Aeronautical Engineering",
            "Bachelor of Telecommunications Engineering",
        ],
        "ECA": [
            "Bachelor of Commerce in Accounting",
            "Bachelor of Commerce in Finance",
        ],
        "EGM": [
            "Bachelor of Arts in Economics and Statistics",
        ],
        "HGE": [
            "Bachelor of Arts in Economics",
        ],
        "HGL": [
            "Bachelor of Laws",
        ],
        "HKL": [
            "Bachelor of Laws",
        ],
    }

    priority_list = programme_priority.get(
        combination.code,
        []
    )

    def sort_programmes(programme):

        name = programme["degree"]

        # Education programmes appear after specialist programmes.

        if name.startswith("Bachelor of Education in "):
            return (1, 0, name)

        if name in priority_list:
            return (0, priority_list.index(name), name)

        return (0, 999, name)

    eligible_programmes.sort(key=sort_programmes)

    # 6. Calculate academic match percentages.

    recommendations = calculate_academic_match(
        grades,
        eligible_programmes,
    )

    # 7. Generate alternative academic guidance if necessary.

    fallback = recommend_fallback(
        eligibility_result,
         combination.code,
    )

    # 8. Display the results.

    return render(
        request,
        "academic/recommendations.html",
        {
            "programmes": eligible_programmes,
            "recommendations": recommendations,
            "fallback": fallback,
            "grades": display_grades,
            "combination": combination.code,
            "total_points": eligibility_result["total_points"],
        },
    )
