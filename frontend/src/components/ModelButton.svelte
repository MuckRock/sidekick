<script>
  import emitter from "@/emit";

  export let status;

  const emit = emitter({
    plus() {},
    minus() {},
    remove() {}
  });

  // SVG assets
  import plusSvg from "@/assets/plus.svg";
  import minusSvg from "@/assets/minus.svg";
</script>

<style lang="scss">
  .modelbuttons {
    :global(svg) {
      display: inline-block;
      vertical-align: middle;
      padding: 0 3px;

      &:hover {
        cursor: pointer;
        transform: scale(1.5);
      }
    }

    button {
      transform: scale(0.8);
      font-weight: bold;

      &.positive {
        background: darken($green, 20%);
        color: lighten($green, 50%);
      }

      &.negative {
        background: darken($brown, 20%);
        color: lighten($brown, 50%);
      }
    }
  }
</style>

<span class="modelbuttons">
  {#if status == 0}
    <span class="button" on:click={emit.plus}>
      {@html plusSvg}
    </span>
    <span class="button" on:click={emit.minus}>
      {@html minusSvg}
    </span>
  {:else}
    <button
      class:positive={status == 1}
      class:negative={status == -1}
      on:click={emit.remove}>
      {#if status == 1}Positive{:else}Negative{/if}
    </button>
  {/if}
</span>
