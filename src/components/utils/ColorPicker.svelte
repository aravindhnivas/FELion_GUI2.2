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

        const setBackgroundColor = (color) => {

            document.documentElement.style.backgroundColor = color
            document.body.style.backgroundColor = color
            jQuery(".navbar.is-dark, .panel-heading").css("background-color", darken(color, 6))

            window.navbarBgColor = darken(color, 4)
            
            jQuery("li.is-active a").css("background-color", window.navbarBgColor)
            jQuery(".box, .row1").css("background-color", lighten(color, 6))

            jQuery("#Navbar").css("background-color", lighten(color, 2))
            jQuery(".menu-list a.is-active").css("background-color", window.navbarBgColor)
            jQuery("hr").css("background-color", window.navbarBgColor)

            // jQuery(".input[disabled]").css("background-color", "white").css("border-color", window.navbarBgColor)

            window.btnHoverBgColor = lighten(color, 4)

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