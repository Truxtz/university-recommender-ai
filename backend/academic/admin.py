
from django.contrib import admin
from .models import (
    Subject,
    Combination,
    CombinationSubject,
    GradeScale,
    DegreeProgramme,
    ProgrammeEligibilityRule,
    ProgrammeSubjectRequirement,
)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")


@admin.register(Combination)
class CombinationAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")


@admin.register(CombinationSubject)
class CombinationSubjectAdmin(admin.ModelAdmin):
    list_display = ("combination", "subject", "is_principal")
    list_filter = ("combination", "is_principal")


@admin.register(GradeScale)
class GradeScaleAdmin(admin.ModelAdmin):
    list_display = ("grade", "points", "is_pass")
    list_filter = ("is_pass",)


@admin.register(DegreeProgramme)
class DegreeProgrammeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(ProgrammeEligibilityRule)
class ProgrammeEligibilityRuleAdmin(admin.ModelAdmin):
    list_display = (
        "degree_programme",
        "combination",
        "minimum_points",
        "maths_subject",
    )
    list_filter = ("combination", "degree_programme")


@admin.register(ProgrammeSubjectRequirement)
class ProgrammeSubjectRequirementAdmin(admin.ModelAdmin):
    list_display = (
        "eligibility_rule",
        "subject",
        "minimum_grade",
    )
    list_filter = ("subject", "minimum_grade")
