
from django.db import transaction
from academic.models import (
    Subject,
    GradeScale,
    CombinationSubject,
    ProgrammeEligibilityRule,
    ProgrammeSubjectRequirement,
)

education_subjects = {
    "Physics": "P",
    "Chemistry": "C",
    "Biology": "B",
    "Geography": "G",
    "Mathematics": "M",
    "Economics": "ECO",
    "Commerce": "COM",
    "Accountancy": "ACC",
    "History": "HIS",
    "English Language": "ENG",
    "Kiswahili": "KIS",
}

specialist_requirements = {
    ("Doctor of Medicine (MD)", "PCB"): ["P", "C", "B"],
    ("Bachelor of Nursing", "PCB"): ["C", "B"],
    ("Bachelor of Nursing", "CBG"): ["C", "B"],
    ("Bachelor of Pharmacy", "PCB"): ["C", "B"],
    ("Bachelor of Pharmacy", "CBG"): ["C", "B"],
    ("Bachelor of Petroleum Engineering", "PCM"): ["P", "C", "M"],
    ("Bachelor of Petroleum Engineering", "PGM"): ["P", "G", "M"],
    ("Bachelor of Aeronautical Engineering", "PCM"): ["P", "C", "M"],
    ("Bachelor of Aeronautical Engineering", "PGM"): ["P", "G", "M"],
    ("Bachelor of Telecommunications Engineering", "PCM"): ["P", "C", "M"],
    ("Bachelor of Telecommunications Engineering", "PGM"): ["P", "G", "M"],
    ("Bachelor of Commerce in Accounting", "ECA"): ["ECO", "COM", "ACC"],
    ("Bachelor of Commerce in Finance", "ECA"): ["ECO", "COM", "ACC"],
    ("Bachelor of Arts in Economics and Statistics", "EGM"): ["ECO", "G", "M"],
    ("Bachelor of Arts in Economics", "HGE"): ["HIS", "G", "ECO"],
}

grade_d = GradeScale.objects.get(grade="D")
updated_rules = 0

with transaction.atomic():

    for rule in ProgrammeEligibilityRule.objects.select_related(
        "degree_programme", "combination"
    ):

        programme_name = rule.degree_programme.name
        combination_code = rule.combination.code

        if programme_name.startswith("Bachelor of Education in "):
            teaching_subject = programme_name.replace(
                "Bachelor of Education in ", ""
            )
            required_codes = [education_subjects[teaching_subject]]

        elif programme_name == "Bachelor of Laws":
            required_codes = list(
                CombinationSubject.objects.filter(
                    combination=rule.combination,
                    is_principal=True
                ).values_list("subject__code", flat=True)
            )

        else:
            required_codes = specialist_requirements.get(
                (programme_name, combination_code), []
            )

        required_subjects = list(
            Subject.objects.filter(code__in=required_codes)
        )

        if len(required_subjects) != len(set(required_codes)):
            raise ValueError(
                f"Missing subject for {programme_name} - {combination_code}"
            )

        required_ids = [subject.id for subject in required_subjects]

        rule.subject_requirements.exclude(
            subject_id__in=required_ids
        ).delete()

        for subject in required_subjects:
            ProgrammeSubjectRequirement.objects.update_or_create(
                eligibility_rule=rule,
                subject=subject,
                defaults={"minimum_grade": grade_d}
            )

        updated_rules += 1

print("Rules updated:", updated_rules)
print(
    "Subject requirements:",
    ProgrammeSubjectRequirement.objects.filter(
        eligibility_rule__isnull=False
    ).count()
)
