<script>
  import MainTemplate from "./templates/MainTemplate";
  import Link from "@/router/Link";
  import { onMount } from "svelte";

  const APP_URL = process.env.APP_URL;

  let loading = true;
  let collections = [];

  onMount(async () => {
    const response = await fetch(APP_URL + "list_collections");
    collections = await response.json();
    loading = false;
  });
</script>

<style lang="scss">
  .collection {
    border: solid 2px $blue;
    max-width: 600px;
    margin: 20px 0;
    padding: 10px 20px;
    box-sizing: border-box;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;

    h1 {
      color: $blue;
      font-size: 18px;
    }

    &:hover {
      background: $blue;
      color: white;
      transform: scale(1.05);

      h1 {
        color: white;
      }
    }
  }
</style>

<MainTemplate>
  <h1>Choose a collection to analyze</h1>

  {#if loading}
    <p>
      <i>Loading...</i>
    </p>
  {:else if collections.length > 0}
    {#each collections as collection}
      <Link to={'collection'} params={{ name: collection.name }}>
        <div class="collection">
          <h1>{collection.name}</h1>
          <ul>
            <li>
              {collection.params.num_documents.toLocaleString()} documents
            </li>
            <li>
              Average word length: {Math.round(collection.params.avg_words).toLocaleString()}
            </li>
          </ul>
        </div>
      </Link>
    {/each}
  {:else}
    <p>No collections were found</p>
  {/if}
</MainTemplate>
