<script>

  import AnimateBox from "./utils/AnimateBox.svelte";
  export let jq;
  let animation_welcome;
  console.log("Loading");
  jq(document).ready(() => {

    jq("#Welcome").css("display", "block");
    
    animation_welcome = anime
      .timeline({ loop: false })
      .add({
        targets: ".ml5 .line",
        opacity: [0.5, 1],
        scaleX: [0, 1],
        easing: "easeInOutExpo",
        duration: 700
      })
      .add({
        targets: ".ml5 .line",
        duration: 600,
        easing: "easeOutExpo",
        translateY: (el, i) => -0.625 + 0.625 * 2 * i + "em"
      })
      .add({
        targets: ".ml5 .letters-left",
        opacity: [0, 1],
        translateX: ["0.5em", 0],
        easing: "easeOutExpo",
        duration: 600,
        offset: "-=300"
      })
      .add({
        targets: ".ml5 .letters-right",
        opacity: [0, 1],
        translateX: ["-0.5em", 0],
        easing: "easeOutExpo",
        duration: 600,
        offset: "-=600"
      })
      .add({
        targets: ".ml5 .letters-subtitle",
        opacity: [0, 1],
        translateX: ["-0.5em", 0],
        easing: "easeOutExpo",
        duration: 600,
        offset: "-=600"
      })
      .add({
        targets: ".ml5",
        opacity: 1,
        duration: 1000,
        easing: "easeOutExpo",
        delay: 1000
      });

  
    const pickr = Pickr.create({
      el: '.color-picker',
      theme: 'classic', // or 'monolith', or 'nano'

      swatches: ["#46307d", "#38236b", "#4a3284", "#5b3ea2"],

      components: {
          preview: true,

          opacity: true,
          hue: true,
          interaction: {

              hex: true,
              rgba: true,
              hsla: true,
              hsva: true,
              cmyk: true,
              input: true,
              clear: false,
              save: true
          }
      }

    })


    const addLight = (color, amount)=>{
      let cc = parseInt(color,16) + amount;
      let c = (cc > 255) ? 255 : (cc);
      c = (c.toString(16).length > 1 ) ? c.toString(16) : `0${c.toString(16)}`;
      return c;
    }

    const lighten = (color, amount)=> {
      color = (color.indexOf("#")>=0) ? color.substring(1,color.length) : color;
      amount = parseInt((255*amount)/100);
      return color = `#${addLight(color.substring(0,2), amount)}${addLight(color.substring(2,4), amount)}${addLight(color.substring(4,6), amount)}`;
    }

    const subtractLight = (color, amount)=>{
      let cc = parseInt(color,16) - amount;
      let c = (cc < 0) ? 0 : (cc);
      c = (c.toString(16).length > 1 ) ? c.toString(16) : `0${c.toString(16)}`;
      return c;
    }

    const darken = (color, amount) =>{
      color = (color.indexOf("#")>=0) ? color.substring(1,color.length) : color;
      amount = parseInt((255*amount)/100);
      return color = `#${subtractLight(color.substring(0,2), amount)}${subtractLight(color.substring(2,4), amount)}${subtractLight(color.substring(4,6), amount)}`;
    }

    const defaultColors = {body:"#46307d", header:"#38236b", navbar:"#4a3284", box:"#5b3ea2"}
    
    let colorChanged = false;
    let newColor;
    let backgroundDefaultColor = defaultColors.body;
    let settingDefaultColor = false;

    const changeStyleByClass = (className, color, amt=6, lightStyle=true) => {
      let element = Array.from(document.getElementsByClassName(className))
      let func;
      lightStyle ? func = lighten : func = darken
      element.forEach(file=>file.style.backgroundColor = func(color, amt))
    }

    const setBackgroundColor = (color) => {
      document.documentElement.style.backgroundColor = color
      document.body.style.backgroundColor = color
      changeStyleByClass("navbar is-dark", color, 6, false)
      changeStyleByClass("box", color)
      changeStyleByClass("panel-heading", color, 6, false)
      changeStyleByClass("row1", color)
      document.getElementById("Navbar").style.backgroundColor = lighten(color, 2)

    }

    pickr.on('hide', instance => {
        colorChanged ? setBackgroundColor(newColor) : setBackgroundColor(backgroundDefaultColor)

    }).on('save', (color, instance) => {

      console.log("Saving new color")
      colorChanged = true
      backgroundDefaultColor = color.toHEXA().toString()

    }).on('change', (color, instance) => {

      colorChanged = false
      newColor = color.toHEXA().toString()

      setBackgroundColor(newColor)

    })

    document.getElementsByClassName("pcr-button")[0].style.border = "solid 1px white"

  });
</script>

<style>

  #Welcome {
    margin-top: 15% !important;
    display: none;
  }

  .ml5 {
    position: relative;
    font-weight: 300;
    font-size: 4.5em;
    color: #fafafa;
  }

  .ml5 .text-wrapper {
    position: relative;
    display: inline-block;
    padding-top: 0.1em;
    padding-right: 0.05em;
    padding-bottom: 0.15em;
    line-height: 1em;
  }

  .ml5 .line {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    margin: auto;
    height: 3px;
    width: 100%;
    background-color: #fafafa;
    transform-origin: 0.5 0;
  }
  .ml5 .letters {
    display: inline-block;
    opacity: 0;
  }
  .letters-subtitle {
    font-size: 0.4em;
  }
</style>

<section class="section" id="Welcome">

  <div class="color-picker"></div>
  <AnimateBox>
    <h1 class="ml5">
      <span class="text-wrapper">
        <span class="line line1" />
        <span class="letters letters-left">FELion</span>
        <span class="letters letters-right">Spectrum Analyser</span>
        <span class="line line2" />
      </span>
      <br />
      <span class="letters letters-subtitle">
        To analyse FELIX data for FELion Instrument
      </span>
    </h1>
  </AnimateBox>
</section>