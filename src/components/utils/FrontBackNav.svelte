<script>
    export let id;
    export let pageName;
    
    function getpage(forward=true) {
        let index = _.indexOf(pageName, id)
        let newID;

        forward ? index += 1 : index -= 1
        if (index >= pageName.length) return console.log("Page END")
        else if (index < 0) return console.log("Page 0")
        else {newID = pageName[index]}

        console.log("Moving to ", newID)
        pageName.forEach(page=>{
            page === newID ? showpage(page) : hidepage(page)
        })
        console.log(pageName)

        localStorage[newID] = document.getElementById(newID+"-name").value
        localStorage["totalPages"] = document.getElementById("numberOfPage").value
    }

</script>
<style lang="scss">
    $ease: cubic-bezier(.2,1,.3,1);
  
    div {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    
    svg {
        fill: white;
        width: 50px;
        height: auto;
        margin: 0 2rem;
        cursor: pointer;
        overflow: visible;
        polygon, path {
        transition: all 0.5s $ease;
        }
        &:hover polygon, &:hover path {
        transition: all 1s $ease;
        fill: #FF4136;
        }
        
        &:hover .arrow {
        animation: arrow-anim 2.5s $ease infinite;
        }
        &:hover .arrow-fixed {
        animation: arrow-fixed-anim 2.5s $ease infinite;
        }
    }
    }

    @keyframes arrow-anim {
        0% {
            opacity: 1;
            transform: translateX(0);
        }
        5% {
            transform: translateX(-0.1rem);
        }
        100% {
            transform: translateX(1rem);
            opacity: 0;
        }
    }

    @keyframes arrow-fixed-anim {
        5% {
            opacity: 0;
        }
        20% {
            opacity: 0.4;
        }
        100% {
            opacity: 1;
        }
    }

</style>

<div class="wrapper">

  <svg on:click="{()=>getpage(false)}" width="18px" height="17px" viewBox="0 0 18 17" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
      <g id="prev" transform="translate(8.500000, 8.500000) scale(-1, 1) translate(-8.500000, -8.500000)">
          <polygon class="arrow" points="16.3746667 8.33860465 7.76133333 15.3067621 6.904 14.3175671 14.2906667 8.34246869 6.908 2.42790698 7.76 1.43613596"></polygon>
          <polygon class="arrow-fixed" points="16.3746667 8.33860465 7.76133333 15.3067621 6.904 14.3175671 14.2906667 8.34246869 6.908 2.42790698 7.76 1.43613596"></polygon>
          <path d="M-1.48029737e-15,0.56157424 L-1.48029737e-15,16.1929159 L9.708,8.33860465 L-2.66453526e-15,0.56157424 L-1.48029737e-15,0.56157424 Z M1.33333333,3.30246869 L7.62533333,8.34246869 L1.33333333,13.4327013 L1.33333333,3.30246869 L1.33333333,3.30246869 Z"></path>
      </g>
  </svg>

  <svg on:click={getpage} width="18px" height="17px" viewBox="-1 0 18 17" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
      <g>
          <polygon class="arrow" points="16.3746667 8.33860465 7.76133333 15.3067621 6.904 14.3175671 14.2906667 8.34246869 6.908 2.42790698 7.76 1.43613596"></polygon>
          <polygon class="arrow-fixed" points="16.3746667 8.33860465 7.76133333 15.3067621 6.904 14.3175671 14.2906667 8.34246869 6.908 2.42790698 7.76 1.43613596"></polygon>
          <path d="M-4.58892184e-16,0.56157424 L-4.58892184e-16,16.1929159 L9.708,8.33860465 L-1.64313008e-15,0.56157424 L-4.58892184e-16,0.56157424 Z M1.33333333,3.30246869 L7.62533333,8.34246869 L1.33333333,13.4327013 L1.33333333,3.30246869 L1.33333333,3.30246869 Z"></path>
      </g>
  </svg>

</div>