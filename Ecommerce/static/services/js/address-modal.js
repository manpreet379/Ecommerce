document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("address-modal");
    const openButton = document.querySelector(".open-modal-button");
    const closeButton = document.querySelector(".close-button");

    openButton.addEventListener("click", function () {
        modal.style.display = "flex";
    });

    closeButton.addEventListener("click", function () {
        modal.style.display = "none";
    });

    // Close modal when clicking outside of it
    window.addEventListener("click", function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });
});
