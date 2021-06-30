<script>
  import { router, Router, currentUrl } from "@/router/router";
  import { routes } from "@/routes";
  import { onMount } from "svelte";
  // Global styles
  import GlobalStyle from "./GlobalStyle";

  // Set up routes
  let resolvedRoute = null;
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
    router.subscribe(() => (resolvedRoute = router.resolvedRoute));
  });

  function handleBackNav(e) {
    router.currentUrl = e.state.path;
  }
</script>

<GlobalStyle />

<svelte:window on:popstate={handleBackNav} />

{#if resolvedRoute != null}
  <svelte:component this={resolvedRoute.component} {...resolvedRoute.props} />
{/if}
