
document.addEventListener("DOMContentLoaded", function () {

    const combinationSelect = document.getElementById("combination");
    const subjectFields = document.querySelectorAll(".subject-field");
    const submitButton = document.getElementById("submit-results");

    function updateSubjects() {

        const selectedCombination = combinationSelect.value;

        subjectFields.forEach(field => {

            const gradeSelect = field.querySelector(".grade-select");

            if (
                selectedCombination !== "" &&
                field.dataset.combination === selectedCombination
            ) {
                field.classList.add("active");
                gradeSelect.disabled = false;
            } else {
                field.classList.remove("active");
                gradeSelect.disabled = true;
                gradeSelect.value = "";
            }

        });

        validateGrades();
    }

    function validateGrades() {

        const selectedCombination = combinationSelect.value;

        const visibleFields = Array.from(subjectFields).filter(field =>
            field.dataset.combination === selectedCombination
        );

        const allGradesSelected = visibleFields.length > 0 &&
            visibleFields.every(field => {
                return field.querySelector(".grade-select").value !== "";
            });

        submitButton.disabled = !allGradesSelected;
    }

    combinationSelect.addEventListener("change", updateSubjects);

    document.querySelectorAll(".grade-select").forEach(select => {
        select.addEventListener("change", validateGrades);
    });

    submitButton.disabled = true;

    updateSubjects();

});
