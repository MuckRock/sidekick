<style lang="scss">
  :global(a) {
    text-decoration: none;
    color: inherit;
  }

  :global(html, body) {
    position: relative;
    width: 100%;
    height: 100%;
    margin: 0;
    padding: 0;
    font-family: "Source Sans Pro", sans-serif;
  }

  :global(button) {
    border: solid 2px black;
    font-family: inherit;
    font-size: 16px;
    padding: 4px 10px;
    font-weight: bold;
    cursor: pointer;
    outline: none;
    vertical-align: middle;

    &:hover {
      transform: scale(1.1);
    }

    &:active {
      transform: scale(1.1) translateY(2px);
    }

    &.smaller {
      transform: scale(0.85);

      &:hover {
        transform: scale(0.9);
      }

      &:active {
        transform: scale(0.9) translateY(2px);
      }
    }
  }
</style>
