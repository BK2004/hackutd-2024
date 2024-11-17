# Modified copy from previous commit of the streamlit_notifications repo on GitHub

from streamlit import runtime
from streamlit.components.v1 import html

def send_push(
    title: str,
    body: str = None,
    icon_path: str = None,
    only_when_on_other_tab: bool = False,
    tag: str = ""
):
    try:
        icon_path_on_server = runtime.get_instance().media_file_mgr.add(icon_path, "image/png", "")
    except:
        icon_path_on_server = icon_path


    variables = f"""
    var title = "{title}";
    var body = "{body}";
    var icon = "{icon_path_on_server}";
    var tag = "{tag}";
    var notificationSent = false; // Flag to track notification state
    """

    script = """
    Notification.requestPermission().then(perm => {
        if (perm === 'granted') {
            notification = new Notification(title, {
                body: body,
                icon: icon,
                tag: tag,
                vibrate: true,
                requireInteraction: true,
            });
            notificationSent = true; // Set the flag to true after sending notification
        } else if (perm === 'denied') {
            console.log('The user refuses to have notifications displayed.');
        } else if (perm === 'default') {
            console.log('The user choice is unknown, so the browser will act as if the value were denied.');
        } else {
            console.log('Unknown permission issue.');
        }
    }).catch(error => {
        console.error('An error occurred while requesting notification permission:', error);
    });
    """

    if only_when_on_other_tab:
        script = """
        let notification;
        document.addEventListener("visibilitychange", () => {{
            if (document.visibilityState === "hidden" && !notificationSent) {{""" + script + """}} else if (document.visibilityState === "visible") {{
                if (notification) {{
                    notification.close();
                }}
                notificationSent = false; // Reset the flag when the tab becomes visible
            }}
        }});
        """
    else:
        pass

    combined = '<script>' + variables + script + '</script>'
    html(combined, width=0, height=0)


def send_alert(message):
    script = '<script>' + f'window.alert("{message}")' + '</script>'
    html(script, width=0, height=0)
