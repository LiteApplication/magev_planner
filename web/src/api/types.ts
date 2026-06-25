type TokenResponse = {
    id: number,
    user_id: number,
    access_token: string,
    expires_at: Date,
    token_type: string
}


type User = {
    id: number,
    email: string,
    full_name: string,
    phone: string,
    admin: boolean,
    group: string
    confirmed: boolean
}


const exampleUser: User = {
    id: -1,
    email: "Loading ...",
    full_name: "Loading ...",
    phone: "",
    admin: false,
    group: "Loading ...",
    confirmed: false
}

type Shop = {
    id: number,
    name: string,
    description: string,
    location: string,
    maps_link: string
    min_time: number,
    max_time: number,
    available_from: string,
    available_until: string
}

type OpenRange = {
    id: number,
    day: number,
    start_time: string,
    end_time: string
}

type ShopWithOpenRange = Shop & {
    open_ranges: OpenRange[]
}

type ReservedTimeRange = {
    id: number,
    start_time: string,
    duration_minutes: number,
    status: number,
    validated: boolean,
    title: string,
    shop: Shop | null
}
const exampleShop: Shop = {
    id: -1,
    name: "",
    description: "",
    location: "",
    maps_link: "https://maps.app.goo.gl/...",
    min_time: 0,
    max_time: 0,
    available_from: "0000-00-00",
    available_until: "0000-00-00"
}

const exampleReservedTimeRange: ReservedTimeRange = {
    id: -1,
    start_time: "1234-56-78 12:00",
    duration_minutes: 90,
    status: -1,
    validated: false,
    title: "Loading ...",
    shop: exampleShop
}

const exampleOpenRange: OpenRange = {
    id: -1,
    day: 0,
    start_time: "00:00",
    end_time: "00:00"
}

const exampleShopWithOpenRange: ShopWithOpenRange = {
    ...exampleShop,
    open_ranges: [exampleOpenRange]
}

type TimeSlot = {
    id: number,
    shop_id: number,
    day: number,
    start_time: string,   // "HH:MM:SS"
    end_time: string,     // "HH:MM:SS"
    max_volunteers: number,
    valid_from: string,   // "YYYY-MM-DD"
    valid_until: string   // "YYYY-MM-DD"
}

type SaveMode = 'all' | 'single' | 'upcoming'

type SlotOp = {
    action: 'create' | 'update' | 'delete',
    slot: Partial<TimeSlot>
}

type SlotStatus = {
    slot: TimeSlot,
    date: string,         // "YYYY-MM-DD"
    booked_count: number,
    booked_by_me: boolean,
    reservation_id: number | null,
    validated: boolean
}

type SlotBooking = {
    reservation_id: number,
    user_id: number,
    full_name: string,
    email: string,
    phone: string,
    group: string,
    validated: boolean
}

type DaySlot = {
    slot: TimeSlot,
    bookings: SlotBooking[]
}

type BookSlotRequest = {
    time_slot_id: number,
    date: string          // "YYYY-MM-DD"
}

type BookMultipleSlotsRequest = {
    time_slot_ids: number[],
    date: string          // "YYYY-MM-DD"
}

type BookRangeRequest = {
    start_time: string,
    duration_minutes: number
}
type Setting = {
    key: string,
    value: string,
    private: boolean
}

type Enterprise = {
    id: number,
    slug: string,
    name: string,
    email_domains: string,
    checkbox_text: string,
    welcome_message: string,
    reminder_message: string
}

// Public subset returned to the (unauthenticated) registration form.
type EnterprisePublic = {
    slug: string,
    name: string,
    email_domains: string,
    checkbox_text: string
}

type Document = {
    id: number,
    filename: string,
    content_type: string,
    size: number,
    url: string
}

type MailTemplate = {
    name: string,
    subject: string,
    content: string,
    default_content: string,
    customized: boolean
}

type Notification = {
    id: number,
    user_id: number | null,
    message: string
    date: string
    data: string,
    icon: string | null,
    is_reminder: boolean,
    read: boolean,
    route: string | null,

    mail: boolean,
    mail_sent: boolean,
}

const exampleNotification: Notification = {
    id: -1,
    user_id: null,
    message: "notification.loading",
    date: "0000-00-00 00:00",
    data: "{}",
    is_reminder: false,
    read: true,
    icon: "pi pi-info-circle",
    route: "/notifications",

    mail: false,
    mail_sent: false,
}



export type { TokenResponse, User, Shop, OpenRange, ShopWithOpenRange, ReservedTimeRange, TimeSlot, SaveMode, SlotOp, SlotStatus, SlotBooking, DaySlot, BookSlotRequest, BookMultipleSlotsRequest, BookRangeRequest, Setting, Enterprise, EnterprisePublic, Document, MailTemplate, Notification }
export { exampleShop, exampleReservedTimeRange, exampleOpenRange, exampleShopWithOpenRange, exampleUser, exampleNotification }