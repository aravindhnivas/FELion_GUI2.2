<script>
  import * as electron from "electron";

  const mainWindow = electron.remote.getCurrentWindow();
  const maximize = () => {
    mainWindow.isFullScreen()
      ? mainWindow.setFullScreen(false)
      : mainWindow.setFullScreen(true);
  };
</script>

<style>
  #header {
    -webkit-user-select: none;
    -webkit-app-region: drag;
  }

  .navbar-item {
    cursor: pointer;
    -webkit-app-region: no-drag;
    color: #fafafa;
  }

  #close:hover {
    background: red;
  }
</style>

<!-- Header -->
<nav class="navbar is-fixed-top is-dark" id="header">

  <div class="navbar-brand">
    <div class="navbar-item">
      <span class="icon">
        <i class="fas fa-chart-pie" />
      </span>
      <span>FELion_GUI2.2</span>
    </div>
  </div>

  <div class="navbar-menu">
    <div class="navbar-end">
      <div class="navbar-item" id="min">
        <i
          class="fas fa-window-minimize"
          on:click={() => mainWindow.minimize()} />
      </div>
      <div class="navbar-item" id="max">
        <i class="fas fa-compress-arrows-alt" on:click={maximize} />
      </div>
      <div class="navbar-item" id="close">
        <i class="fas fa-window-close" on:click={() => mainWindow.close()} />
      </div>
    </div>
  </div>

</nav>
