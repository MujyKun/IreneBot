<template>
  <div
    :class="[
      'flex',
      flipped ? 'lg:flex-row-reverse' : 'lg:flex-row',
      'flex-col',
      'justify-between',
    ]"
  >
    <div :class="['items-start', 'flex', 'flex-col']">
      <slot></slot>
    </div>
    <img :src="src" class="mr-4 max-w-lg" />
  </div>
</template>

<script>
export default {
  name: "CommandSection",
  props: {
    flipped: {
      type: Boolean,
      default: false,
    },
    src: String,
  },
};
</script>