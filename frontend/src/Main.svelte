<script>
  import { router, Router, currentUrl } from "@/router/router";
  import { routes } from "@/routes";
  import { onMount } from "svelte";
  import GlobalStyle from "./GlobalStyle";

  // Set up routes
  router.routes = new Router(...routes);

  onMount(() => {
    router.currentUrl = currentUrl();
    if (!history.state) {
      window.history.replaceState(
        { path: currentUrl() },
        "",
        window.location.href
      );
    }
  });

  function handleBackNav(e) {
    router.currentUrl = e.state.path;
  }
</script>

<GlobalStyle />

<svelte:window on:popstate={handleBackNav} />

{#if $router.resolvedRoute != null}
  <svelte:component
    this={$router.resolvedRoute.component}
    {...$router.resolvedRoute.props} />
{/if}
