
document.addEventListener("DOMContentLoaded", function () {

    // Mobile navigation
    const menuButton = document.querySelector(".menu-toggle");
    const navLinks = document.querySelector(".nav-links");

    if (menuButton && navLinks) {
        menuButton.addEventListener("click", function () {
            const isOpen = navLinks.classList.toggle("open");
            menuButton.setAttribute("aria-expanded", String(isOpen));
            menuButton.textContent = isOpen ? "×" : "☰";
        });

        navLinks.querySelectorAll("a").forEach(link => {
            link.addEventListener("click", function () {
                navLinks.classList.remove("open");
                menuButton.setAttribute("aria-expanded", "false");
                menuButton.textContent = "☰";
            });
        });
    }

    // Review form
    const reviewForm = document.getElementById("reviewForm");
    const fileInput = document.getElementById("codeFile");
    const reviewResults = document.getElementById("reviewResults");
    const analyzeButton = document.getElementById("analyzeButton");

    if (!reviewForm || !fileInput || !reviewResults || !analyzeButton) {
        console.error("Review form elements were not found.");
        return;
    }

    function addText(tag, text, parent) {
        const element = document.createElement(tag);
        element.textContent = text;
        parent.appendChild(element);
        return element;
    }

    function addSection(title, parent) {
        const section = document.createElement("section");
        section.style.marginTop = "22px";

        addText("h3", title, section);
        parent.appendChild(section);

        return section;
    }

    reviewForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const file = fileInput.files[0];

        if (!file) {
            reviewResults.textContent = "Please select a Python file.";
            return;
        }

        if (!file.name.toLowerCase().endsWith(".py")) {
            reviewResults.textContent =
                "Only Python (.py) files are supported.";
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        analyzeButton.disabled = true;
        analyzeButton.textContent = "Analyzing...";
        reviewResults.textContent =
            "Reviewly is checking your code with Python analysis and Gemini AI. Please wait...";

        try {
            const response = await fetch("/upload", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.error || "Code analysis failed.");
            }

            reviewResults.replaceChildren();

            // Basic result summary
            const summary = addSection("Static Code Analysis", reviewResults);

            addText("p", "File: " + data.filename, summary);
            addText(
                "p",
                "Total issues found: " + data.total_issues,
                summary
            );

            // Static findings
            if (!data.findings || data.findings.length === 0) {
                addText(
                    "p",
                    "No common issues were detected by the static analyzer.",
                    summary
                );
            } else {
                data.findings.forEach(function (finding) {
                    const card = document.createElement("div");

                    card.style.padding = "15px";
                    card.style.marginTop = "12px";
                    card.style.border = "1px solid #5965F2";
                    card.style.borderRadius = "12px";
                    card.style.background = "#111A30";

                    addText(
                        "h4",
                        (finding.severity || "Issue") +
                        " - " + (finding.type || "Code Finding"),
                        card
                    );

                    addText("p", finding.message || "", card);
                    addText(
                        "p",
                        "Line: " + (finding.line ?? "Unknown"),
                        card
                    );
                    addText(
                        "p",
                        "Suggestion: " + (finding.suggestion || "Review this code."),
                        card
                    );

                    summary.appendChild(card);
                });
            }

            // Gemini AI review
            const aiSection = addSection("Gemini AI Code Review", reviewResults);

            if (data.ai_review) {
                const aiOutput = document.createElement("div");

                aiOutput.textContent = data.ai_review;
                aiOutput.style.whiteSpace = "pre-wrap";
                aiOutput.style.overflowWrap = "anywhere";
                aiOutput.style.padding = "18px";
                aiOutput.style.marginTop = "12px";
                aiOutput.style.border = "1px solid #36D9C4";
                aiOutput.style.borderRadius = "12px";
                aiOutput.style.background = "#111A30";
                aiOutput.style.lineHeight = "1.7";

                aiSection.appendChild(aiOutput);

            } else {
                addText(
                    "p",
                    "Gemini AI review could not be completed: " +
                    (data.ai_review_error || "Unknown error."),
                    aiSection
                );
            }

        } catch (error) {
            console.error("Review error:", error);
            reviewResults.textContent = "Error: " + error.message;

        } finally {
            analyzeButton.disabled = false;
            analyzeButton.textContent = "Analyze Code →";
        }
    });

});
