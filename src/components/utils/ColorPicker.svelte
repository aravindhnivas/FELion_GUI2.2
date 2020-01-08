<script>
     
    import DraggableDiv from "./DraggableDiv.svelte";
    export let name="color-picker";

    jQuery(document).ready(()=>{
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
    })
</script>

<DraggableDiv id={"color-picker"}>
    <div class={name}></div>
</DraggableDiv>