<template>
  <img :src="src" class="w-full image object-cover h-full" loading="lazy" />
</template>
<script>
export default {
  name: "GalleryImage",
  props: {
    src: String,
  },
};
</script>
<style scoped>
.image {
  max-height: 500px;
  pointer-events: none;
  user-select: none;
  -ms-user-select: none;
  -moz-user-select: none;
  -webkit-user-select: none;
}
</style>