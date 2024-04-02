// Track, style, and (de)activate filters on personal website (matthewfam.com) based on tag interactions.
// Written 2021.

function determineSelectionState(cards, tag) {
    // cycle through cards before doing anything to find out current state
    for (let i = 0; i < cards.length; i++) {
        let card = cards[i];
        let classes = card.className;
        
        // check to see if card is active
        if (classes.includes(`active ${tag}`) === true) {
            alreadyActive = true;
        }

        // check to see if any other cards are active
        let otherClasses = classes.replace(`active ${tag}`, '');
        if (classes.includes(`active `) === true) {
            otherActiveCards = true;
        }
    }
}

function changeSelectionState(cards, tag) {
    // cycle through cards again
    for (let i = 0; i < cards.length; i++) {
        let card = cards[i];
        let classes = card.className;
        let tags = card.getElementsByClassName("tags");

        // if button is being selected, marking card active or hidden marker as is relevant
        if (alreadyActive === false) {
            if (classes.includes(` ${tag}`) === true) {
                card.className = `${classes} active ${tag}`;
                // highlight corresponding tag
                let activeTag = tags[0].querySelector(`[data-tag="${tag}"]`);
                activeTag.classList.add("active");
            } else {
                card.className = `${classes} hide ${tag}`;
            }
        } else {
        // if button is being deselected, remove active or hidden marker as is relevant
            if (classes.includes(`active ${tag}`) === true) {
                let otherClasses = classes.replace(` active ${tag}`, '');
                card.className = otherClasses;
                // unhighlight corresponding tag
                let activeTag = tags[0].querySelector(`[data-tag="${tag}"]`);
                activeTag.classList.remove("active");
            } else {
                let otherClasses = classes.replace(` hide ${tag}`, '');
                card.className = otherClasses;
            }
        }
    }
}

let otherActiveCards = false;
let alreadyActive = false;

async function filterTag(tag) {
    let cards = document.getElementsByClassName("filterDiv");

    await determineSelectionState(cards, tag);
    await changeSelectionState(cards, tag);

    otherActiveCards = false;
    alreadyActive = false;
}

function openFilteredProjects(tag) {
    localStorage.setItem("selectedFilter", tag);
    location.href = "filtered";
}

function openCertiportCertificate() {
    location.href = "assets/documents/Autodesk-Certified-User-AutoCAD.pdf";
}

function filterInit() {
    document.body.addEventListener("click", event => {
        let icon = event.target.closest(".card");
        let button = event.target.closest(".btn");

        if (icon !== null) {
            if (icon.getAttribute("data-tag") !== null) {
                if (icon.getAttribute("data-tag") !== "cad") {
                    openFilteredProjects(icon.getAttribute("data-tag"));
                } else {
                    openCertiportCertificate();
                }
            }
        }
        
        if (button !== null) {
            if (button.getAttribute("data-tag") !== null) {
                filterTag(button.getAttribute("data-tag"));
            }
        }
    })
}

// begin On DOM Load
document.addEventListener("DOMContentLoaded", filterInit);