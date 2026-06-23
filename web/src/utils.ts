import type { ShopWithOpenRange, OpenRange, Shop } from "./api/types";


function timeToMinutes(time: string): number {

    if (time.length === 16 || time.length === 19) { // Extract time from datetime string
        time = time.slice(11, 16);
    }
    else if (time.length === 8) { // HH:MM:SS
        time = time.slice(0, 5);
    }
    else if (time.length !== 5) {
        throw new Error('Invalid time format: ' + time);
    }
    const [hour, minute] = time.split(':').map(Number);
    return hour * 60 + minute;
}
function minutesToTime(minutes: number): string {
    const hour = Math.floor(minutes / 60)
        .toString()
        .padStart(2, '0');
    const minute = (minutes % 60).toString().padStart(2, '0');
    return `${hour}:${minute}`;
}

function reformatTime(time: string): string {
    if (time.length === 16 || time.length === 19) { // Extract time from datetime string
        time = time.slice(11, 16);
    }
    else if (time.length === 8) { // HH:MM:SS
        time = time.slice(0, 5);
    }
    else if (time.length !== 5) {
        throw new Error('Invalid time format: ' + time);
    }
    return time;
}

function DateToMinutes(date: Date): number {
    return date.getHours() * 60 + date.getMinutes();
}

function getDateOfWeek(y: number, w: number) {
    const date = new Date(y, 0, (1 + (w - 1) * 7)); // Elle's method
    date.setDate(date.getDate() + (1 - date.getDay())); // 0 - Sunday, 1 - Monday etc
    // Set the date to Thursday, Wednesday if it is a leap year
    date.setDate(date.getDate() + 2);
    if ((0 == date.getFullYear() % 4) && (0 != date.getFullYear() % 100) || (0 == date.getFullYear() % 400)) {
        date.setDate(date.getDate() - 1);
    }

    return date
}


function getDateOfWeekDay(monday: Date | string, d: number) { // monday is a Date object or a string in the format 'yyyy-mm-dd'
    const date = new Date(monday);
    date.setDate(date.getDate() + d);
    return date;
}

function getWeekDay(date: Date): number {
    return date.getDay() === 0 ? 6 : date.getDay() - 1;
}


function networkDateTime(date: Date) {
    if (!date) {
        date = new Date(0);
    }
    // get local timezone offset
    const date_copy = new Date(date);
    const offset = date.getTimezoneOffset();
    date_copy.setMinutes(date.getMinutes() - offset);

    return date_copy.toISOString().slice(0, 19);
}

function networkDate(date: Date) {
    if (!date) {
        date = new Date(0);
    }
    // get local timezone offset
    const offset = date.getTimezoneOffset();
    date.setMinutes(date.getMinutes() - offset);

    return date.toISOString().slice(0, 10);
}

function date_start_end(start: string, duration_minutes: number, locale: string): { date: string, start: string, end: string } {
    // `start` is a UTC datetime from the backend; render it in the viewer's local time.
    const startDate = parseServerDate(start);
    const endDate = new Date(startDate.getTime() + duration_minutes * 60000);
    const hhmm = (d: Date) => `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
    return {
        date: startDate.toLocaleDateString(locale, {
            weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
        }),
        start: hhmm(startDate),
        end: hhmm(endDate),
    }
}

function validateDates(shopData: ShopWithOpenRange | Shop | null | undefined, startTime: Date, endTime: Date, setError: (a: string | null) => void, day: number, monday: string | Date): boolean {
    if (!shopData) {
        setError('error.shop.not_loaded');
        return false;
    }

    monday = new Date(monday);


    // Do not check the day if it is set to -1 or if the shop's data does not contain open_ranges
    if (day !== -1 && ("open_ranges" in shopData)) {
        const shopStart = (new Date(shopData.available_from)).getTime();
        const shopEnd = (new Date(shopData.available_until)).getTime();

        // Check that the start date is inside an open range
        const open_ranges = shopData?.open_ranges.filter(
            (range: OpenRange) => {
                const rangeDay = getDateOfWeekDay(monday, range.day).getTime();
                return range.day === day && rangeDay >= shopStart && rangeDay <= shopEnd;
            }
        );

        if (!open_ranges.length) {
            setError('error.reservation.not_open_day');
            return false;
        }

        if (!open_ranges.find(
            (range: OpenRange) => {
                const start_time = timeToMinutes(range.start_time);
                const end_time = timeToMinutes(range.end_time);
                const task_time = DateToMinutes(startTime);
                const task_time_end = DateToMinutes(endTime);

                return task_time >= start_time && task_time < end_time && task_time_end <= end_time;
            }
        )) {
            setError('error.reservation.not_open_time');
            return false;
        }
    }

    const timeDiffMinutes = DateToMinutes(endTime) - DateToMinutes(startTime);

    if (timeDiffMinutes < 0) {
        setError('error.reservation.end_before_start');

        return false;
    }


    if (timeDiffMinutes < shopData.min_time) {
        setError('error.reservation.too_short');
        return false;
    }

    if (timeDiffMinutes > shopData.max_time) {
        setError('error.reservation.too_long');
        return false;
    }

    setError(null);
    return true;
}

function formatDate(date: string, locale: string): string {
    const d = new Date(date);
    const options: Intl.DateTimeFormatOptions = {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
    };

    return d.toLocaleDateString(locale, options)
}



function maxDate(date1: Date, date2: Date): Date {
    return date1 > date2 ? date1 : date2;
}

function minDate(date1: Date, date2: Date): Date {
    return date1 < date2 ? date1 : date2;
}

function getMonday(d: Date | string): string {
    // The week starts on Monday
    d = new Date(d);
    const day = d.getDay();
    const diff = d.getDate() - day + (day == 0 ? -6 : 1); // adjust when day is sunday
    // Add the difference to the date
    d.setDate(diff);
    // Cancel out the timezone offset to get the correct format when slicing
    d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
    // Format the day to yyyy-mm-dd
    return d.toISOString().slice(0, 10);
}

// Server timestamps (e.g. notification.date) are stored as naive UTC and serialized
// without a timezone suffix. Mark them as UTC so they render in the viewer's local time.
function parseServerDate(value: string | Date): Date {
    if (value instanceof Date) return value;
    const iso = value.includes('T') ? value : value.replace(' ', 'T');
    const hasTz = /[zZ]$|[+-]\d{2}:?\d{2}$/.test(iso);
    return new Date(hasTz ? iso : iso + 'Z');
}

export {
    timeToMinutes,
    parseServerDate,
    minutesToTime,
    reformatTime,
    getDateOfWeek,
    getDateOfWeekDay,
    DateToMinutes,
    networkDateTime,
    networkDate,
    date_start_end,
    validateDates,
    getWeekDay,
    formatDate,
    getMonday,
    maxDate,
    minDate
};