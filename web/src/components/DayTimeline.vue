<template>
    <div class="timeline rounded-lg border">
        <div class="timeline-header rounded-lg bg-slate-100 dark:bg-slate-800">
            <p>{{ title }}</p><Button @click="$emit('addTask')" severity="info">+</Button>
        </div>
        <div class=" timeline-body divide-y divide-slate-500" :style="cssVars">
            <div v-for="(time, index) in timeIntervals" :key="index" class="time-line"
                @click="index > 0 ? $emit('timeClicked', timeIntervals[index - 1]) : $emit('addTask')">
                <span v-if="time.showLabel" class="time-label text-slate-500">{{ time.label }}</span>
            </div>

        </div>
        <div class="timeline-container" :style="cssVars">
            <div v-for="(task, index) in sortedTasksWithRows" class="task rounded" :class="{ disabled: task.title == null, 'task-selected': task.selected }" :key="index"
                :style="taskStyle(task)" v-tooltip="{
                    value: `<h3 style='font-weight: bold'>${task.title}</h3><p>${task.description}</p>`,
                    escape: false, hideDelay: 0
                }" @click="$emit('clickTask', task)">
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { defineComponent, type PropType } from 'vue';
import { minutesToTime } from '../utils';
import { type Task } from '../types';
import Button from 'primevue/button';

defineEmits<{
    addTask: [];
    clickTask: [task: Task];
    timeClicked: [time: { time: string; showLabel: boolean; label: string }];
}>();
</script>

<script lang="ts">
export default defineComponent({
    name: 'DayTimeline',
    components: {
        // eslint-disable-next-line vue/no-reserved-component-names
        Button
    },
    props: {
        title: {
            type: String,
            required: true
        },
        startOfDay: {
            type: Number,
            required: true
        },
        endOfDay: {
            type: Number,
            required: true
        },
        tasks: {
            type: Object as PropType<Task[]>,
            required: true,
            validator: (tasks: Task[]) =>
                tasks.every(
                    (task) =>
                        'start_time' in task &&
                        'end_time' in task &&
                        'color' in task &&
                        'title' in task &&
                        'description' in task &&
                        'cursor' in task
                )
        },
    },
    computed: {
        timeIntervals() {
            const intervals = [];
            for (let i = this.startOfDay; i <= this.endOfDay; i += 30) {
                intervals.push({
                    time: minutesToTime(i),
                    showLabel: i % 60 === 0,
                    label: this.formatTime(minutesToTime(i))
                });
            }
            return intervals;
        },
        cssVars() {
            return {
                '--subdivisions': this.timeIntervals.length
            };
        },
        sortedTasksWithRows() {
            const sorted: Task[] = this.tasks.map((task) => ({ ...task })).sort((a, b) => a.start_time - b.start_time);
            // Initialize an array to keep track of the end times of the rows
            const rows: number[] = [];
            let availableRows = 0;

            // Iterate through the sorted tasks
            sorted.forEach((task) => {
                let assigned = false;
                if (task.id === null) {
                    task._row = availableRows;
                    availableRows++;
                    assigned = true;
                } else {
                    // Try to assign the task to an existing row
                    for (let i = 0; i < sorted.length; i++) {

                        if (task.start_time >= rows[i]) {
                            task._row = i;
                            rows[i] = task.end_time;
                            assigned = true;
                            break;
                        }
                    }
                }
                // If no existing row is available, create a new row
                if (!assigned) {
                    task._row = rows.length;
                    rows.push(task.end_time);
                }
            });
            return sorted;
        },

    },
    methods: {
        formatTime(time: string) {
            const [hour, minute] = time.split(':');
            return `${hour}:${minute}`;
        },
        taskStyle(task: Task) {
            const totalMinutes =
                this.endOfDay - this.startOfDay + 30;
            const taskStart =
                task.start_time - this.startOfDay + 30;
            const taskEnd =
                task.end_time - this.startOfDay + 30;
            const topPercent = (taskStart / totalMinutes) * 100;
            const heightPercent = ((taskEnd - taskStart) / totalMinutes) * 100;

            const marginLeft = task._row;
            if (task.id === null) {
                return {
                    top: `${topPercent}%`,
                    height: `${heightPercent}%`,
                    backgroundColor: task.color,
                    marginLeft: `${marginLeft}rem`,
                    cursor: task.cursor,
                    zIndex: -1
                };
            }

            return {
                top: `${topPercent}%`,
                height: `${heightPercent}%`,
                backgroundColor: task.color,
                marginLeft: `${marginLeft}rem`,
                cursor: task.cursor
            };
        }
    }
});
</script>

<style scoped>
.timeline {
    width: 10rem;
    min-width: 8em;
    position: relative;
    margin: 1rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: box-shadow 0.3s, width 0.3s;
}

.timeline-header {
    padding: 10px;
    text-align: center;
    font-weight: bold;
    display: flex;
    justify-content: space-between;
}

.timeline-header Button {
    width: 1.5rem;
    height: 1.5rem;
    padding: 0;
    margin: 0;
}

.timeline-body {
    position: absolute;
    overflow: hidden;
    display: grid;
    grid-template-columns: 1fr;
    grid-template-rows: repeat(var(--subdivisions), calc(50rem / var(--subdivisions)));
    width: 100%;
    box-sizing: border-box;
}

.timeline-container {
    position: relative;
    height: 100%;
    width: 100%;
    box-sizing: border-box;
    height: 50rem;
    pointer-events: none;
}

.time-line {
    position: relative;
    display: flex;
    align-items: end;
    height: 100%;
    cursor: default;
}

.time-label {
    font: 0.8rem;
    padding-left: 0.5rem;
}

.task {
    position: absolute;
    left: calc(5 * 0.8rem);
    width: 0.85rem;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    z-index: 3;
    transition: width 0.3s;
    box-sizing: border-box;
    pointer-events: auto;
    margin-top: 2px;
    border-radius: 3px;
}

.task-selected {
    outline: 2px solid white;
    outline-offset: -2px;
    filter: brightness(1.2);
}
</style>
