<template>
  <section class="flex flex-wrap justify-around items-stretch">
    <div class="flex justify-center items-center">
      <Bar class="p-2" :options="chart_options" :data="chart_data" />
    </div>
    <div class="flex justify-center items-center">
      <Bubble class="p-2" :data="bubble_data" :options="chart_options" />
    </div>
    <div class="flex justify-center items-center">
      <Doughnut class="p-2" :data="doughnut_data" :options="chart_options" />
    </div>
    <div class="flex justify-center items-center">
      <Line class="p-2" :data="line_data" :options="chart_options" />
    </div>
    <div class="flex justify-center items-center">
      <Pie class="p-2" :data="pie_data" :options="chart_options" />
    </div>
    <div class="flex justify-center items-center">
      <PolarArea
        class="p-2"
        :data="polararea_data"
        :options="chart_options_l"
      />
    </div>
    <div class="flex justify-center items-center">
      <Scatter class="p-2" :data="scatter_data" :options="chart_options" />
    </div>
    <div class="flex justify-center items-center">
      <Radar class="p-2" :data="radar_data" :options="chart_options_l" />
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useModelStore } from "@/stores/modelStore";
import {
  Bar,
  Bubble,
  Doughnut,
  Line,
  Pie,
  Radar,
  PolarArea,
  Scatter,
} from "vue-chartjs";

import {
  Chart as ChartJS,
  Title,
  Tooltip,
  LineElement,
  Legend,
  BarElement,
  Filler,
  CategoryScale,
  LinearScale,
  PointElement,
  ArcElement,
  RadialLinearScale,
} from "chart.js";

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  Filler,
  BarElement,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  ArcElement,
  RadialLinearScale,
);

const plugins = {
  legend: {
    position: "left",
  },
};

const scatter_data = {
  datasets: [
    {
      label: "Wikis",
      fill: false,
      borderColor: "#f87979",
      backgroundColor: "#f87979",
      data: [
        {
          x: -2,
          y: 4,
        },
        {
          x: -1,
          y: 1,
        },
        {
          x: 0,
          y: 0,
        },
        {
          x: 1,
          y: 1,
        },
        {
          x: 2,
          y: 4,
        },
      ],
    },
    {
      label: "gDocs",
      fill: false,
      borderColor: "#7acbf9",
      backgroundColor: "#7acbf9",
      data: [
        {
          x: -2,
          y: -4,
        },
        {
          x: -1,
          y: -1,
        },
        {
          x: 0,
          y: 1,
        },
        {
          x: 1,
          y: -1,
        },
        {
          x: 2,
          y: -4,
        },
      ],
    },
  ],
};

const polararea_data = {
  labels: ["Epic", "Task", "Story", "Bug", "Design", "Idea", "Issue"],
  datasets: [
    {
      label: "Q1",
      backgroundColor: "rgba(179,181,198,0.2)",
      pointBackgroundColor: "rgba(179,181,198,1)",
      pointBorderColor: "#fff",
      pointHoverBackgroundColor: "#fff",
      pointHoverBorderColor: "rgba(179,181,198,1)",
      data: [65, 59, 90, 81, 56, 55, 40],
    },
    {
      label: "Q2",
      backgroundColor: "rgba(255,99,132,0.2)",
      pointBackgroundColor: "rgba(255,99,132,1)",
      pointBorderColor: "#fff",
      pointHoverBackgroundColor: "#fff",
      pointHoverBorderColor: "rgba(255,99,132,1)",
      data: [28, 48, 40, 19, 96, 27, 100],
    },
  ],
};

const radar_data = {
  labels: ["TSE", "CEA", "SE", "AE", "ENG", "PM", "CSM"],
  datasets: [
    {
      label: "2023",
      backgroundColor: "rgba(179,181,198,0.2)",
      borderColor: "rgba(179,181,198,1)",
      pointBackgroundColor: "rgba(179,181,198,1)",
      pointBorderColor: "#fff",
      pointHoverBackgroundColor: "#fff",
      pointHoverBorderColor: "rgba(179,181,198,1)",
      data: [65, 59, 90, 81, 56, 55, 40],
    },
    {
      label: "2022",
      backgroundColor: "rgba(255,99,132,0.2)",
      borderColor: "rgba(255,99,132,1)",
      pointBackgroundColor: "rgba(255,99,132,1)",
      pointBorderColor: "#fff",
      pointHoverBackgroundColor: "#fff",
      pointHoverBorderColor: "rgba(255,99,132,1)",
      data: [28, 48, 40, 19, 96, 27, 100],
    },
  ],
};

const pie_data = {
  labels: ["Open", "Closed", "In-Progress", "New"],
  datasets: [
    {
      backgroundColor: ["#41B883", "#E46651", "#20A8FF", "#FF4B96"],
      data: [40, 20, 80, 10],
    },
  ],
};

const line_data = {
  labels: [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ],
  datasets: [
    {
      label: "Revenue ($Mil)",
      backgroundColor: "#2600e6",
      data: [40, 39, 10, 40, 39, 80, 40, 40, 39, 10, 40, 39, 80, 40],
      cubicInterpolationMode: "monotone",
      tension: 0.4,
      borderColor: "#2600e6",
    },
    {
      label: "Expenses ($Mil)",
      backgroundColor: "#ff1919",
      data: [20, 29, 4, 41, 29, 70, 35, 20, 29, 4, 41, 29, 70, 35],
      cubicInterpolationMode: "monotone",
      tension: 0.4,
      borderColor: "#ff1919",
    },
  ],
};

const doughnut_data = {
  labels: ["Projects", "Programs", "Portfolios", "Problems"],
  datasets: [
    {
      backgroundColor: ["#41B883", "#E46791", "#00D8FF", "#DD1B16"],
      data: [40, 20, 30, 10],
    },
  ],
};

const bubble_data = ref({
  datasets: [
    {
      label: "Bubble1",
      backgroundColor: "#f87979",
      data: [
        {
          x: 20,
          y: 25,
          r: 5,
        },
        {
          x: 40,
          y: 10,
          r: 10,
        },
        {
          x: 30,
          y: 22,
          r: 30,
        },
      ],
    },
    {
      label: "Bubble2",
      backgroundColor: "#7C8CF8",
      data: [
        {
          x: 10,
          y: 30,
          r: 15,
        },
        {
          x: 20,
          y: 20,
          r: 10,
        },
        {
          x: 15,
          y: 8,
          r: 30,
        },
      ],
    },
  ],
});

const chart_data = ref({
  labels: [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ],
  datasets: [
    {
      label: "Data1",
      backgroundColor: "#f87979",
      data: [40, 20, 12, 39, 10, 40, 39, 80, 40, 20, 12, 11],
    },
    {
      label: "Data2",
      backgroundColor: "#087979",
      data: [20, 30, 22, 19, 15, 60, 29, 75, 45, 30, 16, 18],
    },
  ],
});

const chart_options = ref({
  responsive: true,
  maintainAspectRatio: true,
});

const chart_options_l = ref({
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: {
      position: "left",
    },
  },
});

const modelStore = useModelStore();
</script>
