// Typewriter intro effect for hero section of personal website (matthewfam.com).
// Written 2021.

function wait(delayInMS) {
    return new Promise((resolve) => setTimeout(resolve, delayInMS));
}

async function type(fullTxt, letterDelay = 300, current = '') {
    for (let i = current.innerHTML.length; i < fullTxt.length; i++) {
            await wait(letterDelay);
            if (fullTxt.substring(i, i+6) === '&nbsp;') {
                current.innerHTML = fullTxt.substring(0, i+6);
                i = i + 5;
            } else if (fullTxt.substring(i, i+4) === '&lt;') {
                current.innerHTML = fullTxt.substring(0, i+4);
                i = i + 3;
            } else if (fullTxt.substring(i, i+3) === '&gt') {
                current.innerHTML = fullTxt.substring(0, i+3);
                i = i + 2;
            } else {
                current.innerHTML = fullTxt.substring(0, i+1);
            }   
    }
}

async function backspace(fullTxt, letterDelay = 300, end ='') {
    for (let i = fullTxt.innerHTML.length; i > end.length; i--) {
        await wait(letterDelay);
        if (fullTxt.innerHTML.substring(i-6, i) === '&nbsp;') {
            fullTxt.innerHTML = fullTxt.innerHTML.substring(0, i-6);
            i = i-5;
        } else if (fullTxt.innerHTML.substring(i-4, i) === '&lt;') {
            fullTxt.innerHTML = fullTxt.innerHTML.substring(0, i-4);
            i = i-3;
        } else if (fullTxt.innerHTML.substring(i-3, i) === '&gt') {
            fullTxt.innerHTML = fullTxt.innerHTML.substring(0, i-3);
            i = i-2;
        } else {
            fullTxt.innerHTML = fullTxt.innerHTML.substring(0, i-1);
        }
    }
}

async function typeWriter(speedForward = 1000, speedBackward = 500, betweenDelay = 3000, backToFrontDelay = 0) {
    const identities = {
        dataAnalyst: {
            text: '&nbsp;data analyst.',
            connect: '&nbsp;is a',
            id: 'data-analyst'
        },
        // researcher: {
        //     text: '&nbsp;researcher.',
        //     connect: '&nbsp;is a',
        //     id: 'researcher'
        // },
        coder: {
            text: '&nbsp;&lt;id="developer"&gt.',
            connect: '&nbsp;is a',
            id: 'coder'
        },
        mlEngineer: {
            text: '&nbsp;AI/ML engineer.',
            connect: '&nbsp;is an',
            id: 'researcher'
        },
        scientist: {
            text: '&nbsp;scientist.',
            connect: '&nbsp;is a',
            id: 'scientist'
        },
        writer: {
            text: '&nbsp;writer.',
            connect: '&nbsp;is a',
            id: 'writer'
        },
        artist: {
            text: '&nbsp;artist.',
            connect: '&nbsp;is an',
            id: 'artist'
        // },
        // designer: {
        //     text: '&nbsp;designer.',
        //     connect: '&nbsp;is a',
        //     id: 'designer'
        // },
        // storyteller: {
        //     text: '&nbsp;storyteller.',
        //     connect: '&nbsp;is a',
        //     id: 'storyteller'
        }
    }

    // cycle through identities object to look at each nested identity object separately
    for (identity in identities) {
        
        // make cursor static for motion
        document.getElementById("cursor").style.setProperty("--state", "none");
  
        // get access to html span between tag and identity
        let connector = document.getElementById("is-a");

        // proceed to acccess and fill in appropriate connector text
        if (connector.innerHTML.length === 0) {
            document.getElementById("cursor").style.setProperty("--state", "blink");
            await wait(betweenDelay/3);
            document.getElementById("cursor").style.setProperty("--state", "none");
            await type(identities[identity].connect, speedForward, connector);
        } else if (connector.innerHTML.length > identities[identity].connect.length) {
            // if the current connector is longer than the appropriate connector, delete until it matches;
            await backspace(connector, speedBackward, identities[identity].connect);
        } else if (connector.innerHTML.length < identities[identity].connect.length) {
            await type(identities[identity].connect, speedForward, connector);
        }
       
        // check if identity is coder, since that requires special treatment
        if (identity !== 'coder') {
            // add ID for proper font styling
            let role = document.getElementById("identity");
            role.className = identities[identity].id;

            // fill in corresponding identity html
            await type(identities[identity].text, speedForward, role);

            // make cursor blink while still
            document.getElementById("cursor").style.setProperty("--state", "blink");
            // Add delay between identitiess
            await wait(betweenDelay);
            // make cursor static for motion
            document.getElementById("cursor").style.setProperty("--state", "none");

            // delete the text after a delay
            await backspace(role, speedBackward); //incorporate delay

        } else {
            // if so, access unique coder spans
            let openerTag = document.getElementById("identity");
            let blueText = document.getElementById("coder-blue");
            let coderEqual = document.getElementById("coder-equal");
            let greenText =  document.getElementById("coder-green");
            let closingTag = document.getElementById("coder-end");
            let cursorDefiner = document.getElementById("cursor");

            // change cursor to coding version
            cursorDefiner.className = 'coding-cursor';

            // add ID for proper font styling
            openerTag.className = identities[identity].id;

            // fill coder texts in proper spans
            await type(identities[identity].text.substring(0, 10), speedForward, openerTag);
            await type(identities[identity].text.substring(10, 12), speedForward, blueText);
            await type(identities[identity].text.substring(12, 13), speedForward, coderEqual);
            await type(identities[identity].text.substring(13, 24), speedForward, greenText);
            await type(identities[identity].text.substring(24, identities[identity].text.length), speedForward, closingTag);

            // make cursor blink while still
            document.getElementById("cursor").style.setProperty("--state", "blink");
            // add delay between identitiess
            await wait(betweenDelay);
            // make cursor static for motion
            document.getElementById("cursor").style.setProperty("--state", "none");

            // delete coder text;
            await backspace(closingTag, speedBackward);
            await backspace(greenText, speedBackward);
            await backspace(coderEqual, speedBackward);
            await backspace(blueText, speedBackward);
            await backspace(openerTag, speedBackward);

            // return cursor, text, classes, and ids to previous state
            openerTag.className = '';
            cursorDefiner.className = 'normal-cursor';
        }
        
        // set delay between completion of deleting and beginning of typing new word
        document.getElementById("cursor").style.setProperty("--state", "blink");
        await wait(backToFrontDelay);
    }

    this.typeWriter(speedForward, speedBackward, betweenDelay, backToFrontDelay);
}

// begin on DOM load
document.addEventListener('DOMContentLoaded', () => typeWriter(100, 60, 2000, 1000));