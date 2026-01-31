document.addEventListener("DOMContentLoaded", () => {

    // ----------- HANDLE MEAL REQUESTS -----------
    const requestForms = document.querySelectorAll("form[action^='/api/request/']");

    requestForms.forEach(form => {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            const action = form.getAttribute("action");
            const button = form.querySelector("button");

            try {
                const response = await fetch(action, {
                    method: "POST",
                    credentials: "same-origin",
                });

                const data = await response.json();

                if (response.ok) {
                    alert(data.message);

                    // Update portions available in the list item
                    const portionsElement = form.previousElementSibling;
                    if (portionsElement) {
                        let match = portionsElement.innerText.match(/\d+/);
                        if (match) {
                            let portions = parseInt(match[0]);
                            portions = Math.max(0, portions - 1);
                            portionsElement.innerText = "Portions Available: " + portions;

                            // Disable button if no portions left
                            if (portions <= 0) {
                                button.disabled = true;
                                button.innerText = "No Portions Left";
                            }
                        }
                    }

                } else {
                    alert(data.error || "Error requesting meal.");
                }

            } catch (err) {
                console.error(err);
                alert("Network error while requesting meal.");
            }
        });
    });

    // ----------- OPTIONAL: Image Preview for Cook Form -----------
    const imageInput = document.querySelector("input[type='file'][name='image']");
    if (imageInput) {
        imageInput.addEventListener("change", () => {
            const previewId = "image-preview";
            let preview = document.getElementById(previewId);

            if (!preview) {
                preview = document.createElement("img");
                preview.id = previewId;
                preview.style.width = "150px";
                preview.style.marginTop = "10px";
                imageInput.parentNode.insertBefore(preview, imageInput.nextSibling);
            }

            const file = imageInput.files[0];
            if (file) {
                preview.src = URL.createObjectURL(file);
            }
        });
    }

    // ----------- OPTIONAL: Auto-hide alerts -----------
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.display = "none";
        }, 5000);
    });

});
