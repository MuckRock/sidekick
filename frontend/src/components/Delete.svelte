<script>
  import emitter from "@/emit";

  const emit = emitter({
    delete() {}
  });

  function confirmDelete() {
    if (
      confirm("Are you sure you wish to delete? This action cannot be undone.")
    ) {
      emit.delete();
    }
  }
</script>

<style lang="scss">
  .delete {
    $size: 12px;
    font-size: 12px;
    color: white;
    font-weight: bold;
    text-shadow: 0 0 2px rgba(0, 0, 0, 0.24);
    cursor: pointer;
    user-select: none;
    margin: 0 15px 0 10px;
    background: black;
    width: $size;
    height: $size;
    line-height: $size;
    border-radius: $size / 2;
    text-align: center;
    vertical-align: middle;
    display: inline-block;

    &:hover {
      background: $red;
    }
  }
</style>

<span class="delete" on:click={confirmDelete}>&times;</span>
