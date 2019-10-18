<script>
  export let jq;
  export let currentLocation;
  export let filetag;
  export let updateFolder;
  export let getCheckedFiles;
  export let path;

  let folderFile;
  $: if(!currentLocation) {console.log(`Currentlocation: [${filetag}]: is undefined`)} else {folderFile = updateFolder(currentLocation);}

  const refreshFolder = event => {
    jq(`#${filetag}refreshIcon`).addClass("fa-spin");
    folderFile = updateFolder(currentLocation);
  };

  const changeDir = dir => {
    if (currentLocation == undefined) {
      return console.log("Location undefined");
    }
    jq(`#${filetag}refreshIcon`).addClass("fa-spin");
    currentLocation = path.join(currentLocation, dir);
    jq(`.${filetag}-files`).each((index, val) => (val.checked = false));
  };

  function selectAllToggle(event) {
    jq(`.${filetag}-files`).each((index, val) => {
      let parent = document.getElementsByClassName(val.id)[0];
      if (parent.style.display == "block") {
        val.checked = event.target.checked;
      }
    });
    getCheckedFiles();
  }

  let searchKey;
  const search = () => {
    folderFile.files.forEach(file => {
      let fileParent = document.getElementsByClassName(file)[0];
      file.includes(searchKey)
        ? (fileParent.style.display = "block")
        : (fileParent.style.display = "none");
    });
  };
</script>

<style>
  .filexplorer {
    overflow-y: auto;
    position: absolute;
    max-height: 75vh;
    width: 20%;
  }
  .menu-list {
    padding-left: 2em;
  }
  .menu-label,
  .backbtn,
  .refresh {
    cursor: pointer;
  }

  :focus {
    outline-color: transparent;
  }
</style>

<nav class="panel filexplorer">
  <div class="panel-heading">
    <div class="level">

      <div class="level-left">
        <div class="level-item">
          <span>File Explorer</span>
        </div>
      </div>

      <div class="level-right">
        <div class="level-item">
          <span
            class="icon refresh"
            id="{filetag}refresh"
            on:click={refreshFolder}>
            <i
              class="fas fa-sync refreshIcon"
              id="{filetag}refreshIcon"
              data-tippy="Refresh folder"
              aria-hidden="true" />
          </span>
        </div>
        <div class="level-item">
          <span
            class="icon backbtn"
            id="{filetag}BackButton"
            on:click={() => changeDir('..')}>
            <i
              class="fas fa-angle-left"
              data-tippy="Go back (location)"
              aria-hidden="true" />
          </span>
        </div>
      </div>

    </div>

  </div>

  <div class="panel-block">
    <p class="control has-icons-left">
      <input
        class="input is-small"
        type="text"
        placeholder="Search {filetag} files"
        id="{filetag}-searchFiles"
        bind:value={searchKey}
        on:keyup={search} />
      <span class="icon is-small is-left">
        <i class="fas fa-search" aria-hidden="true" />
      </span>

    </p>
  </div>

  {#if folderFile != undefined}
    <div class="panel-block">
      <aside class="menu" id="{filetag}FileBrowser">

        <div class="menu-label has-text-white" id="{filetag}FolderContainer">
          <span
            class="icon"
            on:click={() => jq(`#${filetag}FileContainer`).toggle()}>
            <i class="fas fa-angle-right" aria-hidden="true" />
          </span>
          <span>{folderFile.parentFolder}</span>
        </div>

        <ul class="menu-list" id="{filetag}FileContainer">

          {#if folderFile.files.length > 0}
            <li>
              <div class="pretty p-icon p-round p-pulse">
                <input
                  type="checkbox"
                  id="{filetag}selectall"
                  on:click={selectAllToggle} />
                <div class="state p-primary">
                  <i class="icon mdi mdi-check" />
                  <label>Select All</label>
                </div>
              </div>
            </li>
          {:else}
            <h1 class="subtitle">No {filetag} files here</h1>
          {/if}

          {#each folderFile.files.sort() as filename}
            <li class={filename} style="display:block;">
              <div class="pretty p-icon p-round p-smooth">
                <input
                  type="checkbox"
                  id={filename}
                  class="{filetag}-files"
                  on:click={getCheckedFiles} />
                <div class="state p-success">
                  <i class="icon mdi mdi-check" />
                  <label for={filename}>{filename}</label>
                </div>
              </div>
            </li>
          {/each}

        </ul>
      </aside>
    </div>

    {#each folderFile.folders as foldername}
      <div class="panel-block">
        <aside class="menu">
          <div class="menu-label has-text-white">
            <span class="icon">
              <i class="fas fa-angle-right" aria-hidden="true" />
            </span>
            <span id={foldername} on:click={() => changeDir(foldername)}>
              {foldername}
            </span>
          </div>
        </aside>
      </div>
    {/each}
  {:else}
    <div class="panel-block">
      <h1 class="subtitle">Browse to load files</h1>
    </div>
  {/if}
</nav>
