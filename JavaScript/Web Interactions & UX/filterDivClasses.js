// Hide cards/projects on personal website (matthewfam.com) based on selected filters.
// Written 2021.

function extractButtonClasses(card) {
    // get buttons in card div
    let btns = card.getElementsByClassName("btn");
    // create empty array to store different button classes
    let filterClasses = []

    // cycle through buttons to extract tag data attributes
    for (let i = 0; i < btns.length; i++) {
        let btn = btns[i];
        let btnTag = btn.getAttribute("data-tag");
        // alternative:
        // let btnTag = btn.dataset.tag

        // store tags in previously collection array
        filterClasses.push(btnTag);
    }

    // filter array for unique tags to use as classes for parent filterDiv
    filterClasses = [... new Set(filterClasses)];

    return filterClasses
}

function setCardClasses() {
    // get all filterable card divs
    let cards = document.getElementsByClassName("filterDiv");

    // cycle through card divs and assign proper classes for filtering based on child buttons
    for (let i = 0; i < cards.length; i++) {
        let card = cards[i];
        let cardClasses = card.classList;

        // extract relevant, unique classes from child buttons
        filterClasses = extractButtonClasses(card);

        // add filtering classes to card
        cardClasses.add(...filterClasses)
        // for browsers without ECMAScript 6 support
        // cardClasses.add.apply(cardClasses, filterClasses) 
    }
}

// begin on DOM load
document.addEventListener("DOMContentLoaded", setCardClasses);