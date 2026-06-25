import type { I18nOptions } from "vue-i18n";

const datetimeFormats: I18nOptions["datetimeFormats"] = {
  "en-US": {
    short: {
      year: "numeric",
      month: "short",
      day: "numeric",
    },
    long: {
      year: "numeric",
      month: "short",
      day: "numeric",
      weekday: "short",
      hour: "numeric",
      minute: "numeric",
    },
    datetime: {
      year: "numeric",
      month: "short",
      day: "numeric",
      weekday: "short",
      hour: "numeric",
      minute: "numeric",
    },
    week: {
      weekday: "short",
      month: "short",
      day: "numeric",
    },
  },
  "fr-FR": {
    short: {
      year: "numeric",
      month: "short",
      day: "numeric",
    },
    long: {
      year: "numeric",
      month: "short",
      day: "numeric",
      weekday: "short",
      hour: "numeric",
      minute: "numeric",
    },
    datetime: {
      year: "numeric",
      month: "short",
      day: "numeric",
      weekday: "short",
      hour: "numeric",
      minute: "numeric",
    },
    week: {
      weekday: "short",
      month: "short",
      day: "numeric",
    },
  },
};

const messages = {
  "en-US": {
    message: {
      hello_world: "hello world",
      login: "Login",
      register: "Register",
      privacy_consent: "Your personal information is used solely to facilitate communication and the management of volunteers within the association. In accordance with data protection regulations, you have the right to access, rectify and delete your data. You may exercise this right at any time by contacting us. Your data is never shared with third parties.",
      reminder_confirmation: "I confirm that I have noted that all information and procedures (volunteer charter and stand information) will be sent to me by reminder email the day before my visit.",
      password_title_set: "Set a new password",
      email: "Email",
      password: "Password",
      confirm_password: "Confirm password",
      full_name: "Full Name",
      phone: "Phone number",
      group: "Group",
      logout: "Logout",
      to_register: "Don't have an account? Register",
      to_login: "Already have an account?",
      save: "Save",
      cancel: "Cancel",
      menu: "Menu",
      select_date: "Select a week",
      all: "All",
      success: "Success",
      empty_list: "Nothing to show here ... yet",
      google_maps: "Google Maps",
      reset_password: "Reset password",
      set_password: "Set password",
      mail_sent:
        "An email has been sent to you with a link to verify your email address. Please verify that you recieved the mail, and check your spam folder if you do not find it after a few minutes.",
      info: "Information",
      add: "Add",
      edit: "Edit",
      delete: "Delete",
      search: "Search",

      date: "Date",
      time: "Time",

      reservation: {
        new_reservation_explanation:
          "Click the button below to show the available shops, then click the 'Book' button to create a reservation in the shop of your choice.",
        new_reservation_button: "Click here to see the shops and book a time",
        booked: "Booked",
        booked_by_you: "Booked by you",
        full: "Full",
        spots_remaining: "{n} spot(s) left",
        past: "Past slot",
        spots_taken: "{booked}/{max} volunteers",
        selected: "Selected (pending)",
        n_selected: "{n} slot(s) selected",
        confirm_booking: "Confirm reservations",
        cancel_booking: "Cancel reservation",
        consecutive_only: "Only consecutive slots on the same day can be selected.",
        deselect_edge: "You can only deselect a slot at the start or end of the selection.",
        manage_slot: "Slot bookings",
        no_bookings: "Nobody has booked this slot yet.",
        remove: "Remove from slot",
        confirm_remove_user: "Remove {name} from this slot?",
        user_removed: "Person removed from the slot.",
        assign_title: "Assign someone to a slot",
        assign: "Assign",
        slot: "Slot",
        person: "Person",
        no_slots_day: "There are no slots on this day.",
        user_assigned: "Person assigned to the slot.",
        edit_title: "Edit reservation",
        edit_description:
          "Please select a new time range for your reservation and click 'Save'",
        add_title: "Add reservation",
        add_description:
          "Please select a time range for your reservation and click 'Save'",
        date: "Date",
        start_time: "Start time",
        end_time: "End time",
        user: "User",
        delete: "Delete",
        confirm_delete:
          "Are you sure you want to delete this reservation?\nThe admins will be notified to try and find a replacement.\nIf you do not want to delete it, click 'Cancel'",
      },
      shops: {
        description: "Gift wrapping operation from\n{from} to\n{until}.",
        open: "Available",
        book: "Book",
        booked: "Booked",
        week_format: "'Week 'WW', 'yy",
        select: "Please select a shop",
      },
    },
    admin: {
      unauthorized: "You are not authorized to view this page",
      admin_column: "Admin",
      confirm_delete_selected_users:
        "Are you sure you want to delete the selected users ?\nThis action cannot be undone.\nTheir reservations will be deleted as well.",
      user_deleted: "The user(s) have been deleted successfully.",
      actions: "Actions",
      password_reset_email_sent:
        "A password reset email has been sent to the user.",
      confirmed_account: "Email confirmed",
      cancel: "Cancel",
      delete: "Delete",
      enterprises: {
        none: "No enterprises yet.",
        add: "Add enterprise",
        edit: "Edit enterprise",
        delete: "Delete enterprise",
        delete_confirm: "Delete the enterprise \"{name}\"? Existing users keep their group label.",
        deleted: "Enterprise deleted.",
        saved: "Enterprise saved.",
        name: "Name",
        name_required: "A name is required.",
        slug: "Slug",
        slug_hint: "Used in the registration link /register/<slug>. Auto-generated from the name if left empty.",
        email_domains: "Email domain(s)",
        email_domains_hint: "Space or comma separated (e.g. magev.fr total.com). Leave empty to accept any email.",
        any_email: "Any email",
        checkbox: "Consent checkbox",
        checkbox_text: "Registration checkbox text (optional)",
        welcome_message: "Welcome email message (optional)",
        reminder_message: "Reminder email message (optional)",
      },
      export: {
        title: "Export planning",
        subtitle:
          "Download a formatted spreadsheet (ODS) of the planning, with one tab per shop and a contact list. Empty volunteer places include a dropdown to fill them in.",
        week: "Upcoming week",
        week_desc: "The current week, from Monday to Sunday.",
        fortnight: "Next 2 weeks",
        fortnight_desc: "The current week and the following one.",
        all: "Until the last reservation",
        all_desc: "Every week from now up to the last booked reservation.",
        download: "Download ODS",
        downloading: "Preparing the file…",
        downloaded: "Planning downloaded.",
        failed: "Could not generate the export.",
      },
      documents: {
        none: "No documents uploaded yet.",
        upload: "Upload",
        uploaded: "Document uploaded.",
        upload_failed: "Upload failed.",
        deleted: "Document deleted.",
        delete: "Delete document",
        delete_confirm: "Delete \"{name}\"? Any email referencing it will break.",
        preview: "Preview",
        filename: "File name",
        type: "Type",
        size: "Size",
        copy_link: "Copy link",
        open: "Open",
        link_copied: "Link copied to clipboard.",
      },
      shop: {
        informations: "Shop informations",
        create: "Create shop",
        delete: "Delete shop",
        name: "Shop name",
        description: "Description",
        location: "Location",
        maps: "Google Maps link",
        min_time: "Minimum reservation time",
        max_time: "Maximum reservation time",
        start_date: "Start date",
        end_date: "End date",

        created: "The shop has been created successfully.",
        updated: "The shop has been updated successfully.",
        deleted: "The shop has been deleted successfully.",
        delete_confirm:
          "Are you sure you want to delete this shop? All reservations will be deleted as well.",

        open_ranges: "Open ranges",
        or_add: "Add an open range",
        or_added: "The open range has been added successfully.",
        or_title: "Open ranges",
        or_day: "Day",
        or_start: "Start time",
        or_end: "End time",
        or_updated: "The open range has been modified successfully.",
        or_deleted: "The open range has been deleted successfully.",

        slots: "Time Slots",
        slot_planner: "Slot Planner",
        slot_details: "Details",
        slot_add: "Draw a slot on the calendar",
        slot_drag_hint:
          "Click and drag to create a slot · Double-click to edit",
        slot_filter_date: "Filter by date",
        slot_max_volunteers: "Max volunteers",
        slot_valid_from: "Valid from",
        slot_valid_until: "Valid until",
        slot_save_all: "Modify all slots",
        slot_save_single: "Modify this slot only",
        slot_save_upcoming: "Modify all upcoming slots",
        slot_created: "Time slot created.",
        slot_updated: "Time slot updated.",
        slot_deleted: "Time slot deleted.",
        slot_delete_confirm:
          "Delete this time slot? All reservations for it will be removed.",
      },
      settings: {
        saved_description: "{key} has been saved successfully.",
        saved_title: "Setting saved",

        optimized_description:
          "The database has been optimized :\n{deleted_tokens} login tokens\n{deleted_password_resets} password reset tokens\n{deleted_reminders} reminders\n{deleted_notifications} notifications\n{deleted_notifications_admin} admin notifications",
        optimized_title: "Database optimized",
        key: "Setting",
        value: "Value",

        title: {
          email_reservation_created: "Send emails to confirm reservations",
          email_reservation_modified: "Send emails on reservation modification",
          email_reservation_cancelled: "Send emails on reservation cancel",
          email_notification_before: "Time before email reminder",
          base_domain: "Server domain name",
          notif_login: "Send notifications on login",
          notif_reservation_created: "Notify user on new reservation",
          notif_admin_reservation_created: "Notify admin on new reservation",
          notif_admin_reservation_cancelled:
            "Notify admin on reservation cancel",
          notif_admin_new_user_created: "Notify admin on new user creation",
          notif_new_user_created: "Notify user when their account is created",
          notif_admin_reservation_modified:
            "Notify admin on reservation modification",
          email_daemon_delay: "Email daemon delay",
          reset_token_validity: "Password reset token validity",
          admin_mail: "Admin email",
          mail_from: "Notification email sender",
          email_admin_reservation_created:
            "Email admins on reservation creation",
          email_admin_reservation_modified:
            "Email admins on reservation modification",
          email_admin_reservation_cancelled:
            "Email admins on reservation cancel",
          email_admin_new_user_created: "Email admins on new user creation",
          block_all_emails: "Block all emails",
          cleanup_reminders_days: "Cleanup reminders",
          cleanup_notifications_days: "Cleanup notifications",
          cleanup_notifications_days_admin: "Cleanup notifications (admin)",
          notify_for_admin_actions: "Notify admins for their own actions",
          api_key: "API key",
          token_validity: "Stay logged in for (h)",
          server_timezone: "Server timezone",
        },
        description: {
          email_reservation_created:
            "When enabled, an email will be sent to the user when this user makes a reservation.",
          email_reservation_modified:
            "When enabled, an email will be sent to the user when this user or an admin modifies their reservation.",
          email_reservation_cancelled:
            "When enabled, an email will be sent to the user when this user or an admin cancels their reservation.",
          email_notification_before:
            "Send an email reminder to the user this many hours before their reservation.<br>Set this to -1 to disable email reminders.",
          base_domain:
            "The domain name of the server. This is used to generate links in emails<br>Be sure to include the protocol (http/https).<br>Do not include a trailing slash. Example: <i>https://reservations.magev.fr</i>.<br><b>Do not modify this setting unless you know what you are doing.</b>",
          notif_login:
            "When enabled, users will receive a notification when they log into the site.",
          notif_reservation_created:
            "When enabled, users will receive a notification each time they create a new reservation.",
          notif_admin_reservation_created:
            "When enabled, admins will receive a notification when someone creates a new reservation",
          notif_admin_reservation_cancelled:
            "When enabled, admins will receive a notification when someone deletes their reservation",
          notif_admin_new_user_created:
            "When enabled, admins will receive a notification when a new user is created",
          notif_new_user_created:
            "When enabled, users will receive a notification when their account is created",
          notif_admin_reservation_modified:
            "When enabled, admins will receive a notification when a user modifies their reservation",
          email_daemon_delay:
            "The maximum amount of time to wait before sending an email. Higher values reduce server load but increase the maximum expected delay in sending emails. <br>Password resets are always sent immediately.",
          reset_token_validity:
            "The validity of the reset token in hours. This is the link sent to the user when they create an account or when you click the 'Reset password' button in the admin page.",
          admin_mail:
            "The email address of the admin. This will be inserted in emails sent to users to contact the admin.",
          mail_from:
            "The email address that will be used as the sender of the notification emails.",
          email_admin_reservation_created:
            "When enabled, admins will receive a notification when a user creates a new reservation.",
          email_admin_reservation_modified:
            "When enabled, admins will receive a notification when a user modifies their reservation.",
          email_admin_reservation_cancelled:
            "When enabled, admins will receive a notification when a user cancels their reservation.",
          email_admin_new_user_created:
            "When enabled, admins will receive a notification when a new user is created.",
          block_all_emails:
            "When enabled, no emails will be sent by the server. This is useful for testing.",
          notify_for_admin_actions:
            "When enabled, all the admins will receive a notification when one of them creates, modifies or deletes a reservation.",
          cleanup_reminders_days:
            "Delete reservation reminders after this many days.",
          cleanup_notifications_days:
            "Delete notifications after this many days.",
          cleanup_notifications_days_admin:
            "Delete admin notifications after this many days.",
          api_key:
            "Key used to get all reservations in the Google Sheets document. This key should be a long random string and should not be shared publicly as it allows access to all reservations.",
          token_validity:
            "The validity of the login tokens in hours. If a user does not use the token within this time, they will have to log in again.",
          server_timezone:
            "IANA timezone name (e.g. Europe/Paris) used to display times in emails and calendar invites. All dates are stored in UTC; this only affects how times are shown to users.",
        },
      },
      reservations: {
        title: "Reservations",
        select_user: "Select a user",
        no_user_selected: "(Keep the same user)",
        filter_no_user_found: "No users found",
        select_shop: "Select a shop",
        filter_no_shop_found: "No shops found",
        no_reservations: "No reservations found",
      },
      mail_templates: {
        insert_button: "Insert a button",
        insert_image: "Insert an image",
        reset: "Reset the template",
        pick_document: "Pick a document",
        customized: "Customized",
        saved: "Template saved successfully.",
        reset_confirm: "Are you sure you want to reset the template?\nThis action cannot be undone.",
        reset_done: "The template has been reset successfully.",
        syntax_help: "Write your email using Markdown syntax. You can insert variables between curly braces, for example {user} will be replaced by the user's name. Use the buttons above to insert an image or a button.",
        test: "Test",
        test_sent: "Test email queued for sending.",
      }
    },
    day: {
      0: "Monday",
      1: "Tuesday",
      2: "Wednesday",
      3: "Thursday",
      4: "Friday",
      5: "Saturday",
      6: "Sunday",
    },
    error: {
      title: "Error",
      unknown: "Something went wrong, please try again later",
      fields: "Please fill all fields",
      server: "Something went wrong on the server. ",
      api_key_not_set: "The API key is not set in the server settings.",
      api_key_invalid: "The API key is invalid.",
      document: {
        too_large: "File is too large (max 25 MB).",
        not_found: "Document not found.",
      },
      token: {
        invalid: "Invalid token",
        expired: "Token expired",
        not_authenticated:
          "Welcome to the site, please enter your email and password to log in, or click on the register button to create an account.",
      },
      admin: {
        required: "Admin role required",
        setting_not_found: "This setting cannot be found",
      },
      auth: {
        user_not_found: "User not found",
        invalid_password: "Invalid credentials",
        email_exists:
          'Email already exists, if you already have an account, click "Login" to register.',
        full_name_too_short: "Full name too short",
        email_invalid: "Invalid email",
        enterprise_invalid: "Unknown enterprise",
        email_domain_mismatch: "Your email address does not match this enterprise.",
        terms_not_accepted: "You must accept the terms to register.",
        privacy_not_accepted: "You must acknowledge the privacy notice to register.",
        reminder_not_accepted: "You must confirm this acknowledgement to set your password.",
        password_too_short: "Password must be at least 8 characters long",
        password_match: "Passwords do not match",
        invalid_reset_token:
          "This password reset link is invalid, please request another.",
        expired_reset_token:
          "This password reset link has expired, please request another.",
        used_reset_token:
          "This password reset link has already been used, please try to log in now.",
      },
      shop: {
        not_found: "Shop not found",
        invalid_week: "Invalid week number",
        negative_time_range: "Time range must be longer than 0",
        time_range_overlap: "Time range overlaps an existing time range",
        time_range_not_found: "Time range not found",
        id_mismatch: "Shop id mismatch",
        not_loaded: "Something went wrong while loading the shop",
        no_id: "No shop id provided",
        unknown: "An unknown error happened while trying to get the shop data.",
      },
      reservation: {
        overlap: "This slot is full",
        not_found: "Reservation not found",
        cant_cancel: "Not allowed to cancel this reservation",
        cant_update: "Not allowed to update this reservation",
        cancel_validated: "Cannot cancel a validated reservation",
        outside_open: "The reservation must be within the shop's opening hours",
        past_time: "Cannot book a time in the past",
        before_open: "Cannot book a time before the shop opens",
        after_close: "Cannot book a time after the shop closes",
        already_booked: "You already have a reservation for this slot",

        end_before_start: "The end time must be after the start time",
        too_short: "The time range must be at least {min_time} minutes",
        too_long: "The time range must be at most {max_time} minutes",
        not_open_day: "The shop does not need volunteers on this day",
        not_open_time: "The shop does not need volunteers at this time",

        unknown:
          "An unknown error happened while trying to book this time range.",
        confirm_cancel: "Cancel your reservation for this slot?",
      },
      slot: {
        not_found: "Time slot not found",
        not_active: "This slot is not active on this date",
        wrong_day: "Slot day does not match the selected date",
        invalid_time: "Start time must be before end time",
        invalid_dates: "Valid from must be before valid until",
      },
      user: {
        not_found: "User not found",
        email_not_same: "Cannot change email",
        cant_set_self_admin: "Cannot change own admin status",
        already_exists: "User already exists",
        unknown: "An unknown error happened while trying to get the user data.",
      },
      notification: {
        unknown:
          "An unknown error happened while trying to get the notifications.",
        not_found: "Notification not found",
        not_allowed: "Not allowed to access this notification",
      },
    },
    menu: {
      my_reservations: "My future reservations",
      create_reservation: "Book a time",
      admin: {
        title: "Admin",
        shops: "Shops",
        users: "Users",
        reservations: "Reservations",
        enterprises: "Enterprises",
        documents: "Documents",
        settings: "Server settings",
        mail_templates: "Mail templates",
        export: "Export planning",
      },
    },
    notification: {
      delete: "Delete",
      mark_as_read: "Mark as read",
      mark_as_unread: "Mark as unread",
      mark_all_as_read: "Mark all as read",
      delete_all: "Delete all",
      delete_all_confirm:
        "Are you sure you want to delete all notifications ?\nThis action cannot be undone.",
      all_deleted: "All notifications have been deleted.",
      cancel: "Cancel",
      success: "Success",

      login: {
        title: "New login",
        body: "You have logged in successfully",
      },
      loading: {
        title: "Loading",
        body: "Loading data ...",
        access: "Please wait",
      },
      test: {
        title: "Test notification {test}",
        body: "This is a test notification",
        access: "Open test",
      },
      welcome_new_user: {
        title: "Welcome to the site",
        body: "Welcome to the site {user}. You can now make reservations to volunteer in the shops by clicking on the 'Book a time' button, and see your future reservations by clicking on the 'My future reservations' button.",
      },
      reservation_created: {
        title: "New reservation",
        body: "You have successfully created a new reservation at {shop} on <strong>{datetime-start_time}</strong> for <strong>{duration}</strong>",
        access: "Open timeline",
      },
      reservation_modified: {
        title: "Reservation modified",
        body: "Your reservation at {shop} on <strong>{datetime-previous_start_time}</strong> for <strong>{previous_duration}</strong> has been modified to <strong>{datetime-start_time}</strong> for <strong>{duration}</strong>",
        access: "Open timeline",
      },
      reservation_cancelled: {
        title: "Reservation cancelled",
        body: "Your reservation at {shop} on <strong>{datetime-start_time}</strong> for <strong>{duration}</strong> has been cancelled",
        access: "Open timeline",
      },
      reservation_reassigned_old: {
        title: "Reservation reassigned",
        body: "Your reservation at {shop} on <strong>{datetime-start_time}</strong> for <strong>{duration}</strong> has been reassigned to another person.",
        access: "Open timeline",
      },
      reservation_reassigned_new: {
        title: "New reservation",
        body: "The reservation at {shop} on <strong>{datetime-start_time}</strong> for <strong>{duration}</strong> has been assigned to you.",
        access: "Open timeline",
      },
      reminder: {
        title: "Reminder",
        body: "You have a reservation at {shop} on <strong>{datetime-start_time}</strong> for <strong>{duration}</strong>",
        access: "Open timeline",
      },
      admin: {
        reservation_created: {
          title: "New reservation",
          body: "<strong>{user}</strong> has created a new reservation at {shop} on <strong>{datetime-start_time}</strong> for <strong>{duration}</strong>",
          access: "Open timeline",
        },
        reservation_modified: {
          title: "Reservation modified",
          body: "<strong>{user}</strong> has modified their reservation at {shop} on <strong>{datetime-previous_start_time}</strong> for <strong>{previous_duration}</strong> to <strong>{datetime-start_time}</strong> for <strong>{duration}</strong>",
          access: "Open timeline",
        },
        reservation_cancelled: {
          title: "Reservation cancelled",
          body: "<strong>{user}</strong> has cancelled their reservation at {shop} on <strong>{datetime-start_time}</strong> for <strong>{duration}</strong>",
          access: "Open timeline",
        },
        new_user: {
          title: "New user",
          body: "<strong>{user}</strong> has created an account with the email <strong>{email}</strong> in the group <strong>{group}</strong>",
          access: "Open users",
        },
      },
    },
    date_locale: "en-US",
  },
  "fr-FR": {
    message: {
      hello_world: "Bonjour le monde",
      login: "Connexion",
      register: "S'inscrire",
      privacy_consent: "Vos informations personelles sont utilisées uniquement pour faciliter la communication et la gestion des bénévoles au sein de l'association. Conformément à la reglementation en matière de protection des données personelles, vous disposez d'un droit d'accès, de rectification et de suppression de vos données. Vous pouvez exercer ce droit à tout moment en nous contactant. Vos données ne sont en aucun cas transmises à des tiers.",
      reminder_confirmation: "Je confirme avoir bien noté que l'ensemble des informations et des procédures (charte des bénévoles et informations sur les stands) me sera envoyé par mail de rappel la veille de ma venue.",
      password_title_set: "Définir un nouveau mot de passe",
      email: "Email",
      password: "Mot de passe",
      confirm_password: "Confirmer le mot de passe",
      full_name: "Prénom et nom",
      phone: "Numéro de téléphone",
      group: "Groupe",
      logout: "Déconnexion",
      to_register: "Vous n'avez pas de compte ? Inscrivez-vous",
      to_login: "Vous avez déjà un compte ?",
      save: "Sauvegarder",
      cancel: "Annuler",
      menu: "Menu",
      select_date: "Sélectionnez une semaine",
      all: "Tous",
      success: "Succès",
      empty_list: "Rien à afficher pour le moment ...",
      google_maps: "Google Maps",
      reset_password: "Réinitialiser le mot de passe",
      set_password: "Définir le mot de passe",
      mail_sent:
        'Un email vous a été envoyé avec un lien pour vérifier votre adresse email. Si vous ne recevez pas le message, vérifiez votre dossier "Indésirables/Spam". ',
      info: "Information",
      add: "Ajouter",
      edit: "Modifier",
      delete: "Supprimer",
      search: "Rechercher",

      date: "Date",
      time: "Heure",

      reservation: {
        new_reservation_explanation:
          "Cliquez sur le bouton ci-dessous pour afficher les magasins disponibles, puis cliquez sur le bouton 'Réserver' pour créer une réservation dans le magasin de votre choix.",
        new_reservation_button:
          "Cliquez ici pour voir les magasins et réserver un créneau",
        booked: "Réservé",
        booked_by_you: "Réservé par vous",
        full: "Complet",
        spots_remaining: "{n} place(s) restante(s)",
        past: "Créneau passé",
        spots_taken: "{booked}/{max} bénévoles",
        selected: "Sélectionné (en attente)",
        n_selected: "{n} créneau(x) sélectionné(s)",
        confirm_booking: "Confirmer les réservations",
        cancel_booking: "Annuler la réservation",
        consecutive_only: "Seuls des créneaux consécutifs sur le même jour peuvent être sélectionnés.",
        deselect_edge: "Vous ne pouvez désélectionner qu'un créneau en début ou fin de sélection.",
        manage_slot: "Réservations du créneau",
        no_bookings: "Personne n'a encore réservé ce créneau.",
        remove: "Retirer du créneau",
        confirm_remove_user: "Retirer {name} de ce créneau ?",
        user_removed: "Personne retirée du créneau.",
        assign_title: "Assigner quelqu'un à un créneau",
        assign: "Assigner",
        slot: "Créneau",
        person: "Personne",
        no_slots_day: "Il n'y a aucun créneau ce jour-là.",
        user_assigned: "Personne assignée au créneau.",
        edit_title: "Modifier la réservation",
        edit_description:
          "Veuillez sélectionner une nouvelle plage horaire pour votre réservation puis cliquez sur 'Sauvegarder'",
        add_title: "Ajouter une réservation",
        add_description:
          "Veuillez sélectionner une plage horaire pour votre réservation puis cliquez sur 'Sauvegarder'",
        date: "Date",
        start_time: "Heure de début",
        end_time: "Heure de fin",
        user: "Utilisateur",
        delete: "Supprimer",
        confirm_delete:
          "Êtes-vous sûr de vouloir supprimer cette réservation ?\nLes administrateurs seront informés pour tenter de trouver un remplaçant.\nSi vous ne souhaitez pas supprimer, cliquez sur 'Annuler'",
      },
      shops: {
        description: "Opération paquets cadeaux du\n{from} au\n{until}.",
        open: "Disponible",
        book: "Réserver",
        booked: "Réservé",
        week_format: "'Semaine 'WW', 'yy",
        select: "Veuillez sélectionner un magasin",
      },
    },
    admin: {
      unauthorized: "Vous n'êtes pas autorisé à voir cette page",
      admin_column: "Admin",
      confirm_delete_selected_users:
        "Êtes-vous sûr de vouloir supprimer les utilisateurs sélectionnés ? Cette action est irréversible. Leurs réservations seront également supprimées.",
      user_deleted: "Les utilisateurs ont été supprimés avec succès.",
      actions: "Actions",
      password_reset_email_sent:
        "Un email de réinitialisation de mot de passe a été envoyé à l'utilisateur.",
      confirmed_account: "Email confirmé",
      cancel: "Annuler",
      delete: "Supprimer",
      enterprises: {
        none: "Aucune entreprise pour le moment.",
        add: "Ajouter une entreprise",
        edit: "Modifier l'entreprise",
        delete: "Supprimer l'entreprise",
        delete_confirm: "Supprimer l'entreprise « {name} » ? Les utilisateurs existants conservent leur groupe.",
        deleted: "Entreprise supprimée.",
        saved: "Entreprise enregistrée.",
        name: "Nom",
        name_required: "Un nom est requis.",
        slug: "Slug",
        slug_hint: "Utilisé dans le lien d'inscription /register/<slug>. Généré depuis le nom si laissé vide.",
        email_domains: "Domaine(s) email",
        email_domains_hint: "Séparés par des espaces ou des virgules (ex. magev.fr total.com). Laisser vide pour accepter tout email.",
        any_email: "Tout email",
        checkbox: "Case de consentement",
        checkbox_text: "Texte de la case à cocher à l'inscription (optionnel)",
        welcome_message: "Message de l'email de bienvenue (optionnel)",
        reminder_message: "Message de l'email de rappel (optionnel)",
      },
      export: {
        title: "Exporter le planning",
        subtitle:
          "Téléchargez un tableur formaté (ODS) du planning, avec un onglet par magasin et une liste de contacts. Les places de bénévoles libres comportent un menu déroulant pour les compléter.",
        week: "Semaine à venir",
        week_desc: "La semaine en cours, du lundi au dimanche.",
        fortnight: "2 prochaines semaines",
        fortnight_desc: "La semaine en cours et la suivante.",
        all: "Jusqu'à la dernière réservation",
        all_desc: "Toutes les semaines à partir de maintenant jusqu'à la dernière réservation.",
        download: "Télécharger l'ODS",
        downloading: "Préparation du fichier…",
        downloaded: "Planning téléchargé.",
        failed: "Impossible de générer l'export.",
      },
      documents: {
        none: "Aucun document téléversé pour le moment.",
        upload: "Téléverser",
        uploaded: "Document téléversé.",
        upload_failed: "Échec du téléversement.",
        deleted: "Document supprimé.",
        delete: "Supprimer le document",
        delete_confirm: "Supprimer « {name} » ? Tout email y faisant référence sera cassé.",
        preview: "Aperçu",
        filename: "Nom du fichier",
        type: "Type",
        size: "Taille",
        copy_link: "Copier le lien",
        open: "Ouvrir",
        link_copied: "Lien copié dans le presse-papiers.",
      },
      shop: {
        informations: "Informations sur le magasin",
        create: "Créer un magasin",
        delete: "Supprimer le magasin",
        name: "Nom de le magasin",
        description: "Description",
        location: "Emplacement",
        maps: "Lien Google Maps",
        min_time: "Temps de réservation minimum",
        max_time: "Temps de réservation maximum",
        start_date: "Date de début",
        end_date: "Date de fin",

        created: "Le magasin a été créée avec succès.",
        updated: "Le magasin a été mise à jour avec succès.",
        deleted: "Le magasin a été supprimée avec succès.",
        delete_confirm:
          "Êtes-vous sûr de vouloir supprimer ce magasin ? Toutes les réservations seront supprimées.",

        open_ranges: "Plages horaires",
        or_add: "Ajouter une plage horaire",
        or_added: "La plage horaire a été ajoutée avec succès.",
        or_title: "Plages horaires",
        or_day: "Jour",
        or_start: "Heure de début",
        or_end: "Heure de fin",
        or_updated: "La plage horaire a été modifiée avec succès.",
        or_deleted: "La plage horaire a été supprimée avec succès.",

        slots: "Créneaux",
        slot_planner: "Planificateur de créneaux",
        slot_details: "Détails",
        slot_add: "Dessinez un créneau sur le calendrier",
        slot_drag_hint:
          "Cliquez et faites glisser pour créer · Double-clic pour modifier",
        slot_filter_date: "Filtrer par date",
        slot_max_volunteers: "Bénévoles max",
        slot_valid_from: "Valide à partir du",
        slot_valid_until: "Valide jusqu'au",
        slot_save_all: "Modifier tous les créneaux",
        slot_save_single: "Modifier ce créneau uniquement",
        slot_save_upcoming: "Modifier les créneaux à venir",
        slot_created: "Créneau créé.",
        slot_updated: "Créneau mis à jour.",
        slot_deleted: "Créneau supprimé.",
        slot_delete_confirm:
          "Supprimer ce créneau ? Toutes les réservations associées seront supprimées.",
      },
      settings: {
        saved_description: "{key} a été sauvegardé avec succès.",
        saved_title: "Paramètre sauvegardé",
        optimized_description:
          "La base de données a été optimisée :\n{deleted_tokens} jetons de connexion\n{deleted_password_resets} jetons de réinitialisation de mot de passe\n{deleted_reminders} rappels\n{deleted_notifications} notifications\n{deleted_notifications_admin} notifications admin",
        key: "Paramètre",
        value: "Valeur",

        title: {
          email_reservation_created:
            "Envoyer des emails pour confirmer les réservations",
          email_reservation_modified:
            "Envoyer des emails lors de la modification de la réservation",
          email_reservation_cancelled:
            "Envoyer des emails lors de l'annulation de la réservation",
          email_notification_before: "Temps avant le rappel par email",
          base_domain: "Nom de domaine du serveur",
          notif_login: "Envoyer des notifications à la connexion",
          notif_reservation_created:
            "Notifier l'utilisateur lors de la création d'une nouvelle réservation",
          notif_admin_reservation_created:
            "Notifier l'admin lors de la création d'une nouvelle réservation",
          notif_admin_reservation_cancelled:
            "Notifier l'admin lors de l'annulation d'une réservation",
          notif_admin_new_user_created:
            "Notifier l'admin lors de la création d'un nouvel utilisateur",
          notif_new_user_created:
            "Notifier l'utilisateur lors de la création de son compte",
          notif_admin_reservation_modified:
            "Notifier l'admin lors de la modification d'une réservation",
          email_daemon_delay: "Délai du démon d'email",
          reset_token_validity:
            "Validité du jeton de réinitialisation du mot de passe",
          admin_mail: "Email de l'admin",
          mail_from: "Expéditeur de l'email de notification",
          email_admin_reservation_created:
            "Envoyer un email aux admins lors de la création d'une réservation",
          email_admin_reservation_modified:
            "Envoyer un email aux admins lors de la modification d'une réservation",
          email_admin_reservation_cancelled:
            "Envoyer un email aux admins lors de l'annulation d'une réservation",
          email_admin_new_user_created:
            "Envoyer un email aux admins lors de la création d'un nouvel utilisateur",
          notify_for_admin_actions:
            "Notifier les admins pour leurs propres actions",
          block_all_emails: "Bloquer tous les emails",
          cleanup_reminders_days: "Nettoyage rappels",
          cleanup_notifications_days: "Nettoyage notifications",
          cleanup_notifications_days_admin: "Nettoyage notifications (admin)",
          api_key: "Clé API",
          token_validity: "Rester connecté pendant (h)",
          server_timezone: "Fuseau horaire du serveur",
        },
        description: {
          email_reservation_created:
            "Lorsque cette option est activée, un email est envoyé à l'utilisateur lorsque celui-ci fait une réservation.",
          email_reservation_modified:
            "Lorsque cette option est activée, un email est envoyé à l'utilisateur lorsque celui-ci ou un admin modifie sa réservation.",
          email_reservation_cancelled:
            "Lorsque cette option est activée, un email est envoyé à l'utilisateur lorsque celui-ci ou un admin annule sa réservation.",
          email_notification_before:
            "Envoyer un rappel par email cet intervalle d'heures avant la réservation.<br>Définir à -1 pour désactiver les rappels par email.",
          base_domain:
            "Le nom de domaine du serveur. Utilisé pour générer les liens dans les emails.<br>Incluez le protocole (http/https).<br>Ne pas inclure de barre oblique à la fin. Exemple : <i>https://reservations.magev.fr</i>.<br><b>Ne modifiez pas ce paramètre à moins de savoir ce que vous faites.</b>",
          notif_login:
            "Lorsque cette option est activée, les utilisateurs recevront une notification lorsqu'ils se connectent au site.",
          notif_reservation_created:
            "Lorsque cette option est activée, les utilisateurs recevront une notification chaque fois qu'ils créent une nouvelle réservation.",
          notif_admin_reservation_created:
            "Lorsque cette option est activée, les admins recevront une notification lorsque quelqu'un crée une nouvelle réservation",
          notif_admin_reservation_cancelled:
            "Lorsque cette option est activée, les admins recevront une notification lorsque quelqu'un supprime sa réservation",
          notif_admin_new_user_created:
            "Lorsque cette option est activée, les admins recevront une notification lorsqu'un nouvel utilisateur est créé",
          notif_new_user_created:
            "Lorsque cette option est activée, les utilisateurs recevront une notification lorsque leur compte est créé",
          notif_admin_reservation_modified:
            "Lorsque cette option est activée, les admins recevront une notification lorsqu'un utilisateur modifie sa réservation",
          email_daemon_delay:
            "Le délai maximum (en secondes) avant l'envoi d'un email.<br>Des valeurs plus élevées réduisent la consommation et augmentent les performances du serveur mais augmentent le délai maximum attendu pour l'envoi des emails. <br>Les réinitialisations de mot de passe sont toujours envoyées immédiatement.",
          reset_token_validity:
            "La validité du jeton de réinitialisation en heures. C'est le lien envoyé à l'utilisateur lorsqu'il crée un compte ou lorsque vous cliquez sur le bouton 'Réinitialiser le mot de passe' dans la page admin.",
          admin_mail:
            "L'adresse email de l'admin. Celle-ci sera insérée dans les emails envoyés aux utilisateurs pour contacter l'admin.",
          mail_from:
            "L'adresse email qui sera utilisée comme expéditeur des emails de notification.",
          email_admin_reservation_created:
            "Lorsque cette option est activée, les admins recevront une notification lorsqu'un utilisateur crée une nouvelle réservation.",
          email_admin_reservation_modified:
            "Lorsque cette option est activée, les admins recevront une notification lorsqu'un utilisateur modifie sa réservation.",
          email_admin_reservation_cancelled:
            "Lorsque cette option est activée, les admins recevront une notification lorsqu'un utilisateur annule sa réservation.",
          email_admin_new_user_created:
            "Lorsque cette option est activée, les admins recevront une notification lorsqu'un nouvel utilisateur est créé.",
          notify_for_admin_actions:
            "Lorsque cette option est activée, tous les admins recevront une notification lorsque l'un d'eux crée, modifie ou supprime une réservation.",
          block_all_emails:
            "Lorsque cette option est activée, aucun email ne sera envoyé par le serveur. Cela est utile pour les tests.",
          cleanup_reminders_days:
            "Supprimer les rappels de réservation après ce nombre de jours.",
          cleanup_notifications_days:
            "Supprimer les notifications après ce nombre de jours.",
          cleanup_notifications_days_admin:
            "Supprimer les notifications des admins après ce nombre de jours.",
          api_key:
            "Clé utilisée pour obtenir toutes les réservations dans le document Google Sheets. Cette clé doit être une longue chaîne de caractères générée aléatoirement et ne doit pas être partagée publiquement car elle permet d'accéder à toutes les réservations.",
          token_validity:
            "La validité des jetons de connexion en heures. Si un utilisateur n'utilise pas le jeton dans ce délai, il devra se reconnecter.",
          server_timezone:
            "Nom de fuseau horaire IANA (par ex. Europe/Paris) utilisé pour afficher les heures dans les emails et les invitations de calendrier. Ce réglage n'affecte que l'affichage des heures pour les utilisateurs.",
        },
      },
      reservations: {
        title: "Réservations",
        select_user: "Sélectionnez un utilisateur",
        no_user_selected: "(Garder le même utilisateur)",
        filter_no_user_found: "Aucun utilisateur trouvé",
        select_shop: "Sélectionnez un magasin",
        filter_no_shop_found: "Aucun magasin trouvée",
        no_reservations: "Aucune réservation trouvée",
      },
      mail_templates: {
        insert_button: "Insérer un bouton",
        insert_image: "Insérer une image",
        reset: "Réinitialiser le modèle",
        reset_confirm: "Êtes-vous sûr de vouloir réinitialiser le modèle ?\nCette action est irréversible.",
        reset_done: "Le modèle a été réinitialisé avec succès.",
        pick_document: "Sélectionner un document",
        customized: "Personnalisé",
        saved: "Modèle sauvegardé avec succès.",
        syntax_help: "Rédigez votre mail en utilisant la syntaxe Markdown. Vous pouvez insérer des variables entre accolades, par exemple {user} sera remplacé par le nom de l'utilisateur. Utilisez les boutons ci-dessus pour insérer une image ou un bouton.",
        test: "Tester",
        test_sent: "Email de test mis en file d'attente d'envoi.",
      }
    },
    day: {
      0: "Lundi",
      1: "Mardi",
      2: "Mercredi",
      3: "Jeudi",
      4: "Vendredi",
      5: "Samedi",
      6: "Dimanche",
    },
    error: {
      title: "Erreur",
      unknown: "Une erreur est survenue, veuillez réessayer plus tard",
      fields: "Veuillez remplir tous les champs",
      server: "Une erreur est survenue sur le serveur. ",
      api_key_not_set:
        "La clé API n'est pas définie dans les paramètres du serveur.",
      api_key_invalid: "La clé API est invalide.",
      document: {
        too_large: "Le fichier est trop volumineux (max 25 Mo).",
        not_found: "Document introuvable.",
      },
      token: {
        invalid: "Votre session a expiré, veuillez vous reconnecter",
        expired: "Votre session a expiré, veuillez vous reconnecter",
        not_authenticated:
          'Bienvenue sur le site, veuillez entrer votre email et votre mot de passe pour vous connecter, ou cliquez sur le bouton "Inscrivez-vous" pour créer un compte.',
      },
      admin: {
        required: "Rôle d'administrateur requis",
        setting_not_found: "Ce paramètre est introuvable",
      },
      auth: {
        user_not_found: "Utilisateur non trouvé",
        invalid_password: "Identifiants invalides",
        email_exists:
          'L\'email existe déjà. Si vous avez déjà créé un compte, cliquez sur "Se connecter".',
        full_name_too_short: "Noms trop courts",
        email_invalid: "Email invalide",
        enterprise_invalid: "Entreprise inconnue",
        email_domain_mismatch: "Votre adresse email ne correspond pas à cette entreprise.",
        terms_not_accepted: "Vous devez accepter les conditions pour vous inscrire.",
        privacy_not_accepted: "Vous devez accepter la notice de confidentialité pour vous inscrire.",
        reminder_not_accepted: "Vous devez confirmer cette information pour définir votre mot de passe.",
        password_too_short:
          "Le mot de passe doit comporter au moins 8 caractères",
        password_match: "Les mots de passe ne correspondent pas",
        invalid_reset_token:
          "Ce lien de réinitialisation de mot de passe est invalide, veuillez en demander un autre.",
        expired_reset_token:
          "Ce lien de réinitialisation de mot de passe a expiré, veuillez en demander un autre.",
        used_reset_token:
          "Ce lien de réinitialisation de mot de passe a déjà été utilisé, veuillez essayer de vous connecter maintenant.",
      },
      shop: {
        not_found: "Magasin introuvable",
        invalid_week: "Numéro de semaine invalide",
        negative_time_range: "La plage horaire doit être supérieure à 0",
        time_range_overlap:
          "La plage horaire se chevauche avec une plage horaire existante",
        time_range_not_found: "Plage horaire introuvable",
        id_mismatch: "Id de magasin non conforme",
        not_loaded: "Une erreur est survenue lors du chargement de le magasin",
        no_id: "Aucun id de magasin fourni",
        unknown:
          "Une erreur inconnue est survenue lors de la récupération des données de le magasin.",
      },
      reservation: {
        overlap: "Ce créneau est complet",
        not_found: "Réservation introuvable",
        cant_cancel: "Non autorisé à annuler cette réservation",
        cant_update: "Non autorisé à mettre à jour cette réservation",
        cancel_validated: "Impossible d'annuler une réservation validée",
        outside_open:
          "La réservation doit être dans les horaires d'ouverture de le magasin",
        past_time: "Impossible de réserver un créneau dans le passé",
        before_open:
          "Impossible de réserver un créneau avant l'ouverture de le magasin",
        after_close:
          "Impossible de réserver un créneau après la fermeture de le magasin",
        already_booked: "Vous avez déjà une réservation pour ce créneau",

        end_before_start: "L'heure de fin doit être après l'heure de début",
        too_short: "La plage horaire doit être d'au moins {min_time} minutes",
        too_long: "La plage horaire doit être au maximum de {max_time} minutes",
        not_open_day: "Pas de besoin en bénévolat ce jour-là",
        not_open_time: "Pas de besoin en bénévolat à cette heure",

        unknown:
          "Une erreur inconnue est survenue lors de la réservation de cette plage horaire.",
        confirm_cancel: "Annuler votre réservation pour ce créneau ?",
      },
      slot: {
        not_found: "Créneau introuvable",
        not_active: "Ce créneau n'est pas actif à cette date",
        wrong_day:
          "Le jour du créneau ne correspond pas à la date sélectionnée",
        invalid_time: "L'heure de début doit être avant l'heure de fin",
        invalid_dates: "La date de début doit être avant la date de fin",
      },
      user: {
        not_found: "Utilisateur non trouvé",
        email_not_same: "Impossible de changer l'email",
        cant_set_self_admin:
          "Impossible de modifier votre propre statut d'administrateur",
        already_exists: "L'utilisateur existe déjà",
        unknown:
          "Une erreur inconnue est survenue lors de la récupération des données de l'utilisateur.",
      },
      notification: {
        unknown:
          "Une erreur inconnue est survenue lors de la récupération des notifications.",
        not_found: "Notification introuvable",
        not_allowed: "Accès non autorisé à cette notification",
      },
    },
    menu: {
      my_reservations: "Mes futures réservations",
      create_reservation: "Réserver un créneau",
      admin: {
        title: "Admin",
        shops: "Magasins",
        users: "Utilisateurs",
        reservations: "Réservations",
        enterprises: "Entreprises",
        documents: "Documents",
        settings: "Paramètres du serveur",
        mail_templates: "Modèles d'email",
        export: "Exporter le planning",
      },
    },
    notification: {
      delete: "Supprimer",
      mark_as_read: "Marquer comme lu",
      mark_as_unread: "Marquer comme non lu",
      mark_all_as_read: "Tout marquer comme lu",
      delete_all: "Tout supprimer",
      delete_all_confirm:
        "Êtes-vous sûr de vouloir supprimer toutes les notifications ?\nCette action est irréversible.",
      all_deleted: "Toutes les notifications ont été supprimées.",
      cancel: "Annuler",
      success: "Succès",

      login: {
        title: "Nouvelle connexion",
        body: "Vous vous êtes connecté avec succès",
      },
      loading: {
        title: "Chargement",
        body: "Chargement des données ...",
        access: "Veuillez patienter",
      },
      test: {
        title: "Notification de test {test}",
        body: "Ceci est une notification de test",
        access: "Ouvrir le test",
      },
      welcome_new_user: {
        title: "Bienvenue sur le site",
        body: "Bienvenue sur le site {user}. Vous pouvez désormais faire des réservations pour être bénévole dans les magasins en cliquant sur le bouton 'Réserver un créneau', et voir vos futures réservations en cliquant sur le bouton 'Mes futures réservations'.",
      },
      reservation_created: {
        title: "Nouvelle réservation",
        body: "Vous avez créé une nouvelle réservation à {shop} le <strong>{datetime-start_time}</strong> pour <strong>{duration}</strong>",
        access: "Ouvrir la timeline",
      },
      reservation_modified: {
        title: "Réservation modifiée",
        body: "Votre réservation à {shop} le <strong>{datetime-previous_start_time}</strong> pour <strong>{previous_duration}</strong> a été modifiée pour <strong>{datetime-start_time}</strong> pour <strong>{duration}</strong>",
        access: "Ouvrir la timeline",
      },
      reservation_cancelled: {
        title: "Réservation annulée",
        body: "Votre réservation à {shop} le <strong>{datetime-start_time}</strong> pour <strong>{duration}</strong> a été annulée",
        access: "Ouvrir la timeline",
      },
      reservation_reassigned_old: {
        title: "Réservation réassignée",
        body: "Votre réservation à {shop} le <strong>{datetime-start_time}</strong> pour <strong>{duration}</strong> a été réassignée à une autre personne.",
        access: "Ouvrir la timeline",
      },
      reservation_reassigned_new: {
        title: "Nouvelle réservation",
        body: "La réservation à {shop} le <strong>{datetime-start_time}</strong> pour <strong>{duration}</strong> vous a été assignée.",
        access: "Ouvrir la timeline",
      },
      reminder: {
        title: "Rappel de réservation",
        body: "Vous avez une réservation à {shop} le <strong>{datetime-start_time}</strong> pour <strong>{duration}</strong>",
        access: "Ouvrir la timeline",
      },
      admin: {
        reservation_created: {
          title: "Nouvelle réservation",
          body: "<strong>{user}</strong> a créé une nouvelle réservation à {shop} le <strong>{datetime-start_time}</strong> pour <strong>{duration}</strong>",
          access: "Ouvrir la timeline",
        },
        reservation_modified: {
          title: "Réservation modifiée",
          body: "<strong>{user}</strong> a modifié sa réservation à {shop} pour le <strong>{datetime-previous_start_time}</strong> de <strong>{previous_duration}</strong> pour le <strong>{datetime-start_time}</strong> de <strong>{duration}</strong>",
          access: "Ouvrir la timeline",
        },
        reservation_cancelled: {
          title: "Réservation annulée",
          body: "<strong>{user}</strong> a annulé sa réservation à {shop} le <strong>{datetime-start_time}</strong> pour <strong>{duration}</strong>",
          access: "Ouvrir la timeline",
        },
        new_user: {
          title: "Nouvel utilisateur",
          body: "<strong>{user}</strong> a créé un compte avec l'email <strong>{email}</strong> dans le groupe <strong>{group}</strong>",
          access: "Ouvrir les utilisateurs",
        },
      },
    },
    date_locale: "fr-FR",
  },
};

const languages: { [key: string]: string } = {
  "en-US": "English",
  "fr-FR": "Français",
};

export { messages as default, languages, datetimeFormats };
