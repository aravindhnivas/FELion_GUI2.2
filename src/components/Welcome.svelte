<script>
	import AnimateBox from "./utils/AnimateBox.svelte"
  export let jq;
  console.log("Loading")
  jq(document).ready(()=>jq("#Welcome").css("display", "block"))
</script>
<style>

  #Welcome {
    margin-top: 15% !important;
    display: none;
  }
  
</style>

<section class="section animated fadeInDown" id="Welcome">

  <AnimateBox>
    <h1 class="title">FELion Spectrum Analyser</h1>
    <h2 class="subtitle">To analyse FELIX data for FELion Instrument.</h2>
  </AnimateBox>

</section>