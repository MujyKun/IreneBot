<template>
  <section class="p-3 py-6 text-blue-100">
    <div class="grid md:grid-flow-col justify-between gap-4 max-w-5xl mx-auto">
      <div>
        <b class="font-semibold">{{ servers }}</b
        >+ servers
      </div>
      <div>
        <b class="font-semibold">{{ users }}</b
        >+ users
      </div>
      <div>
        <b class="font-semibold">{{ commandUsage }}</b
        >+ Commands used
      </div>
      <div>
        <b class="font-semibold">{{ photos }}</b
        >+ Idol Photos
      </div>
    </div>
  </section>
</template>


<script>
export default {
  props: {
    servers: Number,
    users: Number,
    commandUsage: Number,
    photos: Number,
  },
  name: "StatsBar",
};
</script>