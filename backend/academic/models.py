
from django.db import models


class Subject(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class Combination(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.code


class CombinationSubject(models.Model):
    combination = models.ForeignKey(
        Combination,
        on_delete=models.CASCADE,
        related_name="combination_subjects"
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="subject_combinations"
    )

    is_principal = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["combination", "subject"],
                name="unique_combination_subject"
            )
        ]

    def __str__(self):
        return f"{self.combination.code} - {self.subject.name}"


class GradeScale(models.Model):
    grade = models.CharField(max_length=5, unique=True)
    points = models.DecimalField(max_digits=5, decimal_places=2)
    is_pass = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.grade} - {self.points} points"


class DegreeProgramme(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class ProgrammeEligibilityRule(models.Model):
    degree_programme = models.ForeignKey(
        DegreeProgramme,
        on_delete=models.CASCADE,
        related_name="eligibility_rules"
    )

    combination = models.ForeignKey(
        Combination,
        on_delete=models.CASCADE,
        related_name="eligibility_rules"
    )

    minimum_points = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    maths_subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="maths_eligibility_rules"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["degree_programme", "combination"],
                name="unique_programme_combination_rule"
            )
        ]

    def __str__(self):
        return f"{self.degree_programme} - {self.combination}"


class ProgrammeSubjectRequirement(models.Model):
    eligibility_rule = models.ForeignKey(
        ProgrammeEligibilityRule,
        on_delete=models.CASCADE,
        related_name="subject_requirements",
        null=True,
        blank=True
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    minimum_grade = models.ForeignKey(
        GradeScale,
        on_delete=models.PROTECT
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["eligibility_rule", "subject"],
                name="unique_rule_subject_requirement"
            )
        ]

    def __str__(self):
        return (
            f"{self.eligibility_rule} - "
            f"{self.subject}: {self.minimum_grade}"
        )
class University(models.Model):
    name = models.CharField(max_length=255, unique=True)

    ownership = models.CharField(
        max_length=10,
        choices=[
            ("PUBLIC", "Public"),
            ("PRIVATE", "Private"),
        ]
    )

    location = models.CharField(max_length=150)
    official_website = models.URLField(blank=True)

    def __str__(self):
        return self.name


class UniversityProgramme(models.Model):
    duration_years = models.PositiveSmallIntegerField()

    minimum_points = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    is_active = models.BooleanField(default=True)

    degree_programme = models.ForeignKey(
        DegreeProgramme,
        on_delete=models.CASCADE
    )

    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.university} - {self.degree_programme}"