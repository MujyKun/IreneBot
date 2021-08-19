<template>
  <main class="bg-theme flex flex-col overflow-hidden relative landing-section">
    <Navbar />
    <img
      class="z-0 bottom-0 left-0 top-0 w-full right-0 mx-auto absolute lg:opacity-70 opacity-40 max-h-full self-end object-cover h-full"
      style="object-position: 58% center"
      src="./wall.jpg"
    />
  </main>
</template>

<script>
import InviteButton from "./InviteButton.vue";
import PatreonButton from "./PatreonButton.vue";
import Navbar from "./Navbar.vue";
import StatsBar from "./StatsBar";

var axios = require('axios');

var config = {
  method: 'get',
  url: 'https://api.irenebot.com/botinfo/'
};


export default {
  components: { InviteButton, StatsBar, Navbar, PatreonButton },
  name: "LandingHeader",
  methods: {
    getLiveData(){
      return axios(config)
        .then(response => {
          this.idol_photo_count = response.data.idol_photo_count;
          this.member_count = response.data.member_count;
          this.server_count = response.data.server_count;
          this.total_commands_used = response.data.total_commands_used;
          }
        )
        .catch(function (error) {
          console.log(error);
        });
    }
  },
  data() {
    return {
      visible: false,
      idol_photo_count: 0,
      member_count: 0,
      server_count: 0,
      total_commands_used: 0
    };
  },
  created() {
    this.getLiveData();
  },
  mounted() {
    setTimeout(() => {
      console.log("Mount");
      this.visible = true;
    }, 2000);
  },
};
</script>

<style scoped>
.landing-section {
  min-height: 100vh;
}
.list-item {
  display: inline-block;
  margin-right: 10px;
}
.list-enter-active,
.list-leave-active {
  transition: all 1s;
}
.list-enter, .list-leave-to /* .list-leave-active below version 2.1.8 */ {
  opacity: 0;
  transform: translateY(30px);
}
</style>