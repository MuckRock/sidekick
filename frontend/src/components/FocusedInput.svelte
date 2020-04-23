<script>
  import { onMount } from "svelte";
  import emitter from "@/emit";

  export let value;

  const emit = emitter({
    enter() {},
    esc() {}
  });

  function handleKeypress(e) {
    if (e.code == "Enter") {
      emit.enter();
    } else if (e.code == "Escape") {
      emit.esc();
    }
  }

  let input;

  onMount(() => {
    input.focus();
  });
</script>

<input bind:value bind:this={input} on:keydown={handleKeypress} {...$$props} />
