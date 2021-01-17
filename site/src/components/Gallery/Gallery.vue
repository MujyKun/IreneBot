<template>
  <section class="bg-theme px-6 overflow-hidden">
    <div class="max-w-6xl mx-auto flex flex-col mb-8">
      <h1 class="text-3xl mb-2 font-bold text-gray-300">
        An endless gallery of kpop idols you love
      </h1>
      <h2 class="text-xl text-gray-400 mb-4">
        Kpop stans like you have looked at {{ photoPulls }} images.
      </h2>
      <!-- <template #addons>
        <navigation />
        <pagination />
      </template> -->
    </div>
    <Carousel
      class="w-full justify-center mb-4 max-h-lg relative overflow-hidden"
      :wrapAround="true"
      :breakpoints="breakpoints"
    >
      <Slide
        draggable="false"
        v-for="image in images"
        :key="image"
        class="select-none"
      >
        <GalleryImage :src="image" class="select-none" />
      </Slide>
    </Carousel>
    <div class="max-w-6xl mx-auto">
      <p class="text-sm text-blueGray-500">Drag images to look around</p>
    </div>
  </section>
</template>

<script>
import "vue3-carousel/dist/carousel.css";
import { Carousel, Slide, Pagination, Navigation } from "vue3-carousel";
import GalleryImage from "./GalleryImage";
export default {
  components: { GalleryImage, Carousel, Slide, Pagination, Navigation },
  props: {
    photoPulls: Number,
  },
  data() {
    return {
      breakpoints: {
        700: {
          itemsToShow: 3.5,
          wrapAround: true,
        },
        // 1024 and up
        1024: {
          itemsToShow: 4,
        },
        1400: {
          itemsToShow: 7.5,
        },
      },
      images: [
        require("./jiu.png"),
        require("./iubutnotreally.png"),
        require("./hug.png"),
        require("./hug.png"),
        require("./jiu2.png"),
        require("./irene.jpg"),
        require("./jiu2.png"),
        require("./irene.jpg"),
        require("./hug.png"),
        require("./jiu2.png"),
        require("./irene.jpg"),
        require("./irene.jpg"),
      ],
    };
  },
};
</script>

<style scoped>
.image-gallery-layout {
  /* grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); */
  margin: 0 -50vw;
  left: 50%;
  right: 50%;
  width: 100vw;
  position: relative;
  pointer-events: stroke;
}
.carousel__track > * {
  /* margin-right: 10px; */
}
</style>