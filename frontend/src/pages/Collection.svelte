<script>
  import MainTemplate from "./templates/MainTemplate";

  import FocusedInput from "@/components/FocusedInput";
  import Delete from "@/components/Delete";
  import ModelButton from "@/components/ModelButton";

  import { onMount, tick } from "svelte";
  import { router } from "@/router/router";

  const APP_URL = process.env.APP_URL;

  let tags = ["Default tag"];
  let documents = [];
  let tagsChanged = false;

  let error = false;

  let addingTag = false;
  let newTag = "";

  const DISPLAY_ADDENDUM = 100;
  const DEFAULT_DISPLAY_LIMIT = 100;
  let displayLimit = DEFAULT_DISPLAY_LIMIT;

  const POSITIVE_CONSTRAINT_VALUE = 1;
  const NEGATIVE_CONSTRAINT_VALUE = 0;

  async function showMore() {
    const wasExpanded = allExpanded;
    displayLimit += 100;
    await tick();
    if (wasExpanded) expandCollapseAll(true);
  }

  $: displayedDocs = documents.slice(0, displayLimit);
  $: moreToShow = displayedDocs.length < documents.length;

  function normalize(tag) {
    return tag.trim();
  }

  function valid(tag) {
    return tag.length > 0 && !tags.includes(tag);
  }

  function addTag() {
    if (addingTag) {
      newTag = normalize(newTag);
      if (valid(newTag)) {
        tags = [...tags, newTag];
      }
      cancelTag();
    } else {
      addingTag = true;
    }
  }

  function cancelTag() {
    addingTag = false;
    newTag = "";
  }

  let documentTags = {};

  function expandConstraints(documentTags) {
    const tags = Object.keys(documentTags);
    const constraints = {};
    const positiveDocs = {};

    tags.forEach((tag) => {
      constraints[tag] = [];
      positiveDocs[tag] = [];
      const documents = Object.keys(documentTags[tag] || {}).map((idx) =>
        parseInt(idx)
      );

      for (let i = 1; i < documents.length; i++) {
        const d1 = documents[i];
        const v1 = documentTags[tag][d1];
        if (v1 == null || v1 == 0) continue;
        for (let j = 0; j < i; j++) {
          // Iterate all pairwise constraints
          const d2 = documents[j];
          const v2 = documentTags[tag][d2];

          if (v1 == 1 && v2 == 1) {
            constraints[tag].push([d1, d2, POSITIVE_CONSTRAINT_VALUE]);
          } else if ((v1 == -1 && v2 == 1) || (v1 == 1 && v2 == -1)) {
            constraints[tag].push([d1, d2, NEGATIVE_CONSTRAINT_VALUE]);
          }
        }
      }

      // Add positive docs
      for (let i = 0; i < documents.length; i++) {
        const d = documents[i];
        if (documentTags[tag][d] == 1) positiveDocs[tag].push(d);
      }
    });

    console.log("constraints", { constraints, positiveDocs });
    console.log("document tags", documentTags);

    return { constraints, positiveDocs };
  }

  $: pairwiseConstraints = expandConstraints(documentTags);

  function assignTag(document, tag, number) {
    const tagAssignments = documentTags[tag] || {};
    tagAssignments[document] = number;
    documentTags[tag] = tagAssignments;
    tagsChanged = true;
  }

  function assignPositiveTag(document, tag) {
    assignTag(document, tag, 1);
  }

  function assignNegativeTag(document, tag) {
    assignTag(document, tag, -1);
  }

  function unassignTag(document, tag) {
    assignTag(document, tag, 0);
  }

  const documentExpansions = {};

  $: allExpanded = displayedDocs.every(
    (doc) =>
      documentExpansions[doc.index] != null &&
      documentExpansions[doc.index].expanded
  );

  async function expandRetract(
    document,
    forceExpand = false,
    forceRetract = false
  ) {
    // Retract if expanded
    if (documentExpansions[document.index] != null) {
      documentExpansions[document.index] = {
        ...documentExpansions[document.index],
        expanded: forceExpand
          ? true
          : forceRetract
          ? false
          : !documentExpansions[document.index].expanded,
      };
      return;
    }

    const collectionName = router.resolvedRoute.props.name;
    const response = await fetch(
      APP_URL +
        `get_document?collection=${encodeURIComponent(
          collectionName
        )}&document=${encodeURIComponent(document.name)}`
    );
    const text = await response.json();
    if (text == null) return;
    documentExpansions[document.index] = {
      expanded: true,
      contents: text,
    };
    return;
  }

  function expandCollapseAll(forceExpand = false) {
    if (forceExpand || !allExpanded) {
      // Expand all
      displayedDocs.forEach((doc) => expandRetract(doc, true));
    } else {
      // Retract all
      displayedDocs.forEach((doc) => expandRetract(doc, false, true));
    }
  }

  let docPercentiles = null;
  let docPercentileDict = {};

  let loading = false;
  async function updateModel() {
    try {
      const collectionName = router.resolvedRoute.props.name;
      loading = true;
      const response = await fetch(
        APP_URL +
          `update_tags?collection=${encodeURIComponent(collectionName)}`,
        {
          method: "post",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(pairwiseConstraints),
        }
      );
      const { dists, percentiles, percentileDicts } = await response.json();
      docPercentiles = percentiles;
      docPercentileDict = percentileDicts;
      tagsChanged = false;

      if (lastSort != null) {
        // Restore sort
        sort(...lastSort);
      } else {
        // Sort by first tag
        defaultTagSort(tags[0]);
      }
      loading = false;
    } catch (e) {
      tagsChanged = false;
      error = true;
      loading = false;
    }
  }

  let lastSort = null;

  function sort(tagName, descending = true) {
    if (docPercentiles == null) return;

    documents = documents.sort((a, b) => {
      const p1 = docPercentileDict[tagName][a.index];
      const p2 = docPercentileDict[tagName][b.index];
      return (p1 - p2) * (descending ? -1 : 1);
    });
    lastSort = [tagName, descending];
  }

  function shuffle(a) {
    // From https://stackoverflow.com/a/6274381
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  function shuffleDocs() {
    documents = shuffle(documents);
    lastSort = null;
  }

  function defaultTagSort(tagName) {
    if (lastSort == null || lastSort[0] != tagName) {
      sort(tagName, true);
    } else {
      sort(tagName, !lastSort[1]);
    }
  }

  onMount(async () => {
    const collectionName = router.resolvedRoute.props.name;
    if (!collectionName) {
      error = true;
      return;
    }

    const response = await fetch(
      APP_URL +
        `list_documents?collection=${encodeURIComponent(collectionName)}`
    );
    const rawDocuments = await response.json();
    documents = rawDocuments.map((document, index) => ({
      index,
      name: document,
    }));
  });

  async function handleKeypress(e) {
    if (e.code == "Semicolon" && e.altKey) {
      // Easter egg: auto-load reasonable demo data for FBI docs
      tags = ["Responsive", "Nonresponsive", "Threats"];
      documentTags = {
        Responsive: {
          "9": -1,
          "18": -1,
          "24": -1,
          "27": -1,
          "31": -1,
          "35": -1,
          "36": -1,
          "42": -1,
          "43": -1,
          "44": -1,
          "51": -1,
          "61": -1,
          "62": -1,
          "64": -1,
          "65": -1,
          "66": -1,
          "67": 1,
          "68": 1,
          "72": -1,
          "80": 1,
          "82": -1,
          "83": 1,
          "84": 1,
          "86": -1,
          "87": -1,
          "89": -1,
          "92": -1,
          "93": 1,
          "97": 1,
          "98": 1,
          "99": 1,
        },
        Nonresponsive: {
          "9": 1,
          "18": 1,
          "24": 1,
          "27": 1,
          "31": 1,
          "35": 1,
          "36": 1,
          "42": 1,
          "43": 1,
          "44": 1,
          "51": 1,
          "61": 1,
          "62": 1,
          "64": 1,
          "65": 1,
          "66": 1,
          "67": -1,
          "68": -1,
          "72": 1,
          "80": -1,
          "82": 1,
          "83": -1,
          "84": -1,
          "86": 1,
          "87": 1,
          "89": 1,
          "92": 1,
          "93": -1,
          "97": -1,
          "98": -1,
          "99": -1,
        },
        Threats: {
          "11": 1,
          "12": 1,
          "13": 1,
          "14": 1,
          "15": 1,
          "16": 1,
          "17": 1,
        },
      };
    } else if (e.code == "KeyM" && e.altKey) {
      await updateModel();
    }
  }
</script>

<style lang="scss">
  :global(input) {
    border: solid 2px black;
    outline: none;
    font-family: inherit;
    font-size: 15px;
    padding: 2px 6px;
  }

  button {
    background: $red;
    color: white;
    margin: 0 10px;

    &.gray {
      background: gray;
      margin-left: -7px;
    }

    &.yellow {
      background: $yellow;
      color: black;
      margin-left: -10px;
      margin-right: 10px;
    }
  }

  .tagschanged {
    padding: 1px 20px 19px 20px;
    background: lighten($yellow, 30%);
    max-width: 500px;
    border-radius: 4px;
    border: solid 2px black;
    margin-top: 21px;
  }

  .documents {
    margin-top: 20px;

    textarea {
      width: 100%;
      max-width: 400px;
      height: 150px;
      font-family: monospace;
      border: solid 2px black;
      padding: 10px;
      margin: 6px 0;
      background: $yellow;
      box-sizing: border-box;
    }

    .docname {
      cursor: pointer;
      display: block;
      padding: 7px 0;
      user-select: none;

      &:hover {
        color: $blue;
        font-weight: bold;
      }
    }

    .tag {
      display: inline-block;
      vertical-align: middle;
      user-select: none;
      cursor: pointer;

      &.active {
        color: $blue;
      }

      .sorter {
        font-size: 9px;
        margin-left: 3px;
      }

      &:hover {
        opacity: 0.8;
      }
    }

    .tagcell {
      user-select: none;

      &.positive {
        background: lighten($green, 50%);
      }

      &.negative {
        background: lighten($brown, 50%);
      }
    }

    table {
      table-layout: fixed;

      td,
      th {
        padding: 4px 10px;
        text-align: left;
        border: solid 1px black;

        &:first-child {
          border-left: none;
        }

        &:last-child {
          border-right: none;
        }
      }

      th {
        &.noborder {
          border: none;
        }

        &.norightborder {
          border-right: none;
        }
      }

      tr:first-child {
        td,
        th {
          border-top: none;
        }
      }

      tr:last-child {
        td,
        th {
          border-bottom: none;
        }
      }
    }
  }

  .shim {
    position: fixed;
    background: rgba(255, 255, 255, 0.7);
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 9;
  }
</style>

<MainTemplate>
  {#if loading}
    <div class="shim" />
  {/if}
  <h1>Tag your documents</h1>

  {#if tagsChanged}
    <div class="tagschanged">
      <p>You have made some changes. Hit update model to reorder the table.</p>
      <div>
        <button on:click={updateModel}>Update model</button>
      </div>
    </div>
  {/if}

  <div class="documents">
    {#if error}
      <div class="loading">An unexpected error occurred</div>
    {:else if documents.length == 0}
      <div class="loading">Loading documents...</div>
    {:else}
      <table cellspacing="0">
        <tr>
          <th>
            <button class="yellow smaller" on:click={() => expandCollapseAll()}>
              {#if allExpanded}Collapse{:else}Expand{/if}
              all
            </button>
            <button class="yellow smaller" on:click={shuffleDocs}>
              Shuffle docs
            </button>
          </th>
          {#each tags as tag, i}
            <th class:norightborder={i == tags.length - 1}>
              <span
                class="tag"
                on:click={() => defaultTagSort(tag)}
                class:active={lastSort != null && lastSort[0] == tag}
              >
                {tag}
                <span class="sorter">
                  {#if lastSort != null && lastSort[0] == tag}
                    {#if lastSort[1]}▼{:else}▲{/if}
                  {/if}
                </span>
              </span>
              {#if tags.length != 1}
                <Delete
                  disabled={tags.length == 1}
                  on:delete={() => {
                    tags = [...tags.slice(0, i), ...tags.slice(i + 1)];
                  }}
                />
              {/if}
            </th>
          {/each}
          <th class="noborder">
            {#if addingTag}
              <FocusedInput
                on:enter={addTag}
                on:esc={cancelTag}
                bind:value={newTag}
                placeholder="Type in tag..."
              />
              <button class:smaller={addingTag} on:click={addTag}>
                + Add tag
              </button>
              <button class="gray smaller" on:click={cancelTag}>Cancel</button>
            {:else}
              <button class="smaller" on:click={addTag}>+ Add tag</button>
            {/if}
          </th>
        </tr>
        {#each displayedDocs as document}
          <tr>
            <td class="document">
              <span class="docname" on:click={() => expandRetract(document)}>
                {document.name}
              </span>
              {#if documentExpansions[document.index] != null && documentExpansions[document.index].expanded}
                <div>
                  <textarea>
                    {documentExpansions[document.index].contents}
                  </textarea>
                </div>
              {/if}
            </td>
            {#each tags as tag}
              <td
                class="tagcell"
                class:positive={documentTags[tag] &&
                  documentTags[tag][document.index] == 1}
                class:negative={documentTags[tag] &&
                  documentTags[tag][document.index] == -1}
              >
                {#if docPercentileDict[tag] != null}
                  {(docPercentileDict[tag][document.index] * 100).toFixed(2)}%
                {/if}
                <ModelButton
                  status={documentTags[tag]
                    ? documentTags[tag][document.index] || 0
                    : 0}
                  on:plus={() => assignPositiveTag(document.index, tag)}
                  on:minus={() => assignNegativeTag(document.index, tag)}
                  on:remove={() => unassignTag(document.index, tag)}
                />
              </td>
            {/each}
          </tr>
        {/each}
      </table>
      {#if moreToShow}
        <p>
          <button on:click={showMore}>Show more</button>
        </p>
      {/if}
    {/if}
  </div>
</MainTemplate>

<svelte:window on:keypress={handleKeypress} />
