<template>
  <section class="max-w-6xl mx-auto">
    <!-- <img src="https://images.irenebot.com/commands/groupmembers/card.png" /> -->
    <command-section
      src="https://images.irenebot.com/commands/groupmembers/callingidols.png"
      class="mb-12"
    >
      <h2
        class="text-4xl font-semibold text-blueGray-300 mb-3 flex items-center"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          width="32"
          height="32"
          class="fill-current mr-3"
        >
          <path fill="none" d="M0 0h24v24H0z" />
          <path
            d="M4.828 21l-.02.02-.021-.02H2.992A.993.993 0 0 1 2 20.007V3.993A1 1 0 0 1 2.992 3h18.016c.548 0 .992.445.992.993v16.014a1 1 0 0 1-.992.993H4.828zM20 15V5H4v14L14 9l6 6zm0 2.828l-6-6L6.828 19H20v-1.172zM8 11a2 2 0 1 1 0-4 2 2 0 0 1 0 4z"
          />
        </svg>
        Find images of your biases
      </h2>
      <p class="text-blueGray-400 w-1/2 text-lg">
        Get images of specific idols or discover new idols by looking at random
        images.
      </p>
    </command-section>
    <command-section
      flipped
      src="https://images.irenebot.com/commands/groupmembers/groups.png"
    >
      <h2
        class="text-4xl font-semibold text-blueGray-300 mb-3 flex items-center"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          width="32"
          height="32"
          class="fill-current mr-2"
        >
          <path fill="none" d="M0 0h24v24H0z" />
          <path
            d="M3 10H2V4.003C2 3.449 2.455 3 2.992 3h18.016A.99.99 0 0 1 22 4.003V10h-1v10.001a.996.996 0 0 1-.993.999H3.993A.996.996 0 0 1 3 20.001V10zm16 0H5v9h14v-9zM4 5v3h16V5H4zm5 7h6v2H9v-2z"
          />
        </svg>
        Get Kpop information
      </h2>
      <p class="text-blueGray-400 w-1/2 text-lg">
        Get images of specific idols or discover new idols by looking at random
        images.
      </p>
    </command-section>
  </section>
</template>

<script>
import CommandSection from "./CommandSection.vue";

export default {
  components: { CommandSection },
  name: "Commands",
};
</script>