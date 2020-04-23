<script>
  import Link from "@/router/Link";
</script>

<style lang="scss">
  header {
    background: $red;
    color: white;
    font-family: Bangers, sans-serif;
    margin: 0;
    padding: 10px 30px;
    font-size: 18px;
    letter-spacing: 2px;
    border-bottom: solid 4px $yellow;
  }

  .content {
    padding: 10px 30px;

    :global(h1) {
      font-size: 20px;
    }
  }
</style>

<header>
  <Link to="home">
    <h1>Sidekick</h1>
  </Link>
</header>

<div class="content">
  <slot />
</div>
