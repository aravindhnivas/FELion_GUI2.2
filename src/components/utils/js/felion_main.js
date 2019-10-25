'use strict'
import { program } from './modules.js';

const successAnimation = "is-success bounce faster";
const dangerAnimation = "is-danger shake faster";
const loadAnimation = "is-loading is-link";


function felixbtntoggle(toggle="none"){

    $("#theoryBtn").css("display", toggle);
    $("#norm_tkplot").css("display", toggle);

}

function runPlot({ fullfiles, filetype, btname, pyfile, filetag=null, args = [], plotArea = "", normethod = true }) {

    let obj = {
        files: fullfiles,

        filetype: filetype,
        mainbtn: `#${btname}`,
        pyfile: pyfile,

        filetag:filetag,
        args: args,
        plotArea: plotArea,
        normethod: normethod

    };

    let $target = $(obj.mainbtn);
    console.log(":: runPlot -> $target", $target);

    $target.addClass("is-loading");

    if (filetype == "felix") {felixbtntoggle("none")}

    return new Promise((resolve, reject)=>{
        let start = new program(obj)
        start.filecheck()
            .then(filecheckResult => {

                console.log(filecheckResult); //Filecheck completed

                start.run()
                    .then((plotResult) => {

                        console.log(plotResult); //Graph plotted
                        $target.removeClass(loadAnimation).addClass(successAnimation);
                        if (filetype == "felix") { felixbtntoggle("block") }
                        resolve(plotResult)
                    })
                    .catch(pythonError => {
                        console.log(pythonError) // Error from python while graph plotting
                        $target.removeClass(loadAnimation).addClass(dangerAnimation);
                        reject(new Error(pythonError))
                    })
            })
            .catch(filecheckError => {
                console.log("FileCheck error: ", filecheckError);  //Filecheck error
                $target.removeClass(loadAnimation).addClass(dangerAnimation)
                reject(new Error(filecheckError))
            })
    })
}

$(document).on('animationend', '.funcBtn', (event) => {
    let $target = $(event.target);
    $target.addClass("is-link");
    if ($target.hasClass("shake")) $target.removeClass(dangerAnimation);
    if ($target.hasClass("bounce")) $target.removeClass(successAnimation);
});

export { runPlot };