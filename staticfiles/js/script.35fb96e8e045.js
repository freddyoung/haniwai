document.addEventListener("DOMContentLoaded", function () {
    const galleryImages = document.querySelectorAll(".gallery-img");
    const lightbox = document.getElementById("lightbox");
    const lightboxImg = document.getElementById("lightbox-img");
    const closeBtn = document.querySelector(".close");
    const prevBtn = document.querySelector(".prev");
    const nextBtn = document.querySelector(".next");
    const imageCounter = document.getElementById("image-counter");

    let currentIndex = 0;

    function updateImage(index) {
        const images = [...galleryImages];
        if (index >= 0 && index < images.length) {
            lightboxImg.src = images[index].src;
            imageCounter.innerText = `${index + 1} / ${images.length}`;
            currentIndex = index;
        }
    }

    galleryImages.forEach((img, index) => {
        img.addEventListener("click", function () {
            lightbox.style.display = "flex";
            updateImage(index);
        });
    });

    closeBtn.addEventListener("click", function () {
        lightbox.style.display = "none";
    });

    prevBtn.addEventListener("click", function () {
        updateImage(currentIndex - 1);
    });

    nextBtn.addEventListener("click", function () {
        updateImage(currentIndex + 1);
    });

    // ✅ Close lightbox when clicking outside image
    lightbox.addEventListener("click", function (e) {
        if (e.target === lightbox) {
            lightbox.style.display = "none";
        }
    });

    // ✅ Keyboard navigation
    document.addEventListener("keydown", function (e) {
        if (lightbox.style.display === "flex") {
            if (e.key === "ArrowRight") updateImage(currentIndex + 1);
            if (e.key === "ArrowLeft") updateImage(currentIndex - 1);
            if (e.key === "Escape") lightbox.style.display = "none";
        }
    });
});
