<script>
    export let pageName
    function getpage(event) {
        let id = event.target.innerHTML
        pageName.forEach(page=>{
            page === id ? showpage(page) : hidepage(page)
        })
    }
</script>

<style lang="scss">
    label {
    .menu {
        position: absolute;
        right: -100px;
        top: -100px;
        z-index: 100;
        width: 200px;
        height: 200px;
        background: #FFF;
        border-radius: 50% 50% 50% 50%;
        transition: .5s ease-in-out;
        box-shadow: 0 0 0 0 #FFF, 0 0 0 0 #FFF;
        cursor: pointer;
    }
    .hamburger {
        position: absolute;
        top: 135px;
        left: 50px;
        width: 30px;
        height: 2px;
        background: #000;
        display: block;
        transform-origin: center;
        transition: .5s ease-in-out;
        &:after,
        &:before {
        transition: .5s ease-in-out;
        content: "";
        position: absolute;
        display: block;
        width: 100%;
        height: 100%;
        background: #000;
        }
        &:before {
        top: -10px;
        } 
        &:after {
        bottom: -10px;
        }
    }
    input {
        display: none;
    }
    input:checked + .menu {
        box-shadow: 0 0 0 100vw #FFF, 0 0 0 100vh #FFF;
        border-radius: 0;
        .hamburger {
        transform: rotate(45deg);
        &:after {
            transform: rotate(90deg);
            bottom: 0;
        }
        &:before {
            transform: rotate(90deg);
            top: 0;
        }
        }
    }
    
    input:checked + .menu + ul {
        opacity: 1;
    }
    
    ul {
        z-index: 200;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%,-50%);
        opacity: 0;
        transition: .25s 0s ease-in-out;
    }
    
    a {
        margin-bottom: 1em;
        display: block;
        color: #000;
        text-decoration: none;
    }
    }

    div {
        color: black;
        cursor: pointer;
    }
</style>

<label>
  <input type="checkbox" />
  <span class="menu"><span class="hamburger"></span></span>
  <ul>
    {#each pageName as item}
        <div on:click={getpage}>{item}</div>
    {/each}
  </ul>
</label>