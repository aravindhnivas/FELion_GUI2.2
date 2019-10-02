'use strict'
import { program } from './modules.js';

const successAnimation = "is-success bounce faster";
const dangerAnimation = "is-danger shake faster";
const loadAnimation = "is-loading is-link";


function runPlot({ fullfiles, filetype, btname, pyfile, args = [], plotArea = "", normethod = true }) {

    let obj = {
        files: fullfiles,

        filetype: filetype,
        mainbtn: `#${btname}`,
        pyfile: pyfile,
        args: args,

        plotArea: plotArea,
        normethod: normethod

    };

    let $target = $(obj.mainbtn);
    console.log(":: runPlot -> $target", $target);

    $target.addClass("is-loading");
    $(`#${filetype}loading`).css("display", "block");
    if (filetype == "felix") { $("#theoryBtn").css("display", "none"); $("#theoryRow").css("display", "none") }

    let start = new program(obj)
    start.filecheck()
        .then(filecheckResult => {

            console.log(filecheckResult); //Filecheck completed

            start.run()
                .then((plotResult) => {

                    console.log(plotResult); //Graph plotted

                    $(`#${filetype}loading`).css("display", "none")
                    $target.removeClass(loadAnimation).addClass(successAnimation);
                    if (filetype == "felix") { $("#theoryBtn").css("display", "block") }
                })
                .catch(pythonError => {
                    $(`#${filetype}loading`).css("display", "none")
                    console.log(pythonError) // Error from python while graph plotting
                    $target.removeClass(loadAnimation).addClass(dangerAnimation);
                })
        })
        .catch(filecheckError => {
            $(`#${filetype}loading`).css("display", "none")
            console.log("FileCheck error: ", filecheckError);  //Filecheck error
            $target.removeClass(loadAnimation).addClass(dangerAnimation)
        })
}

$(document).on('animationend', '.funcBtn', (event) => {
    let $target = $(event.target);
    $target.addClass("is-link");
    if ($target.hasClass("shake")) $target.removeClass(dangerAnimation);
    if ($target.hasClass("bounce")) $target.removeClass(successAnimation);
});

export { runPlot };