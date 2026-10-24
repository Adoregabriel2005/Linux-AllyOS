import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    width: 1280; height: 800
    color: "#191c1e"
    property bool english: config.Language === "en" ? true : config.Language === "pt_BR" ? false : Qt.locale().name.indexOf("pt") !== 0
    property bool preview: String(config.PreviewMode).toLowerCase() === "true"
    function label(pt, en) { return english ? en : pt }
    function signIn() {
        if (preview) { feedback.text = label("Prévia visual: login desativado.", "Visual preview: sign-in disabled."); return }
        if (user.text.length === 0) { user.forceActiveFocus(); return }
        feedback.text = label("Autenticando…", "Signing in…")
        sddm.login(user.text, password.text, sessions.currentIndex)
    }
    Image {
        anchors.fill: parent
        source: "background.png"
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
    }
    Rectangle { anchors.fill: parent; color: "#660c1214" }
    Rectangle {
        width: Math.min(430, root.width - 32)
        height: Math.min(root.height - 30, form.implicitHeight + 40)
        anchors.centerIn: parent
        color: "#ed191c1e"
        border.color: "#646b69"
        ScrollView {
            id: scroller
            anchors.fill: parent; anchors.margins: 20
            contentWidth: availableWidth
            clip: true
            ColumnLayout {
                id: form
                width: scroller.availableWidth
                spacing: root.height < 600 ? 8 : 13
                Label { text: config.systemName; color: "#eee7dc"; font.pixelSize: root.height < 600 ? 26 : 38; font.bold: true }
                Label { text: config.baseLabel; color: "#b9c7bf"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                Label {
                    visible: root.preview
                    text: root.label("PRÉVIA VISUAL · não faz login na conta", "VISUAL PREVIEW · does not sign in")
                    color: "#f3c6c1"; wrapMode: Text.WordWrap; Layout.fillWidth: true
                }
                Button {
                    id: languageButton
                    text: root.english ? "Português" : "English"
                    onClicked: root.english = !root.english
                    background: Rectangle { color: "#30383a"; border.color: "#596161" }
                    contentItem: Text { text: languageButton.text; color: "#eee7dc"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                }
                Rectangle { color: "#c58f9d"; Layout.fillWidth: true; height: 2 }
                Label { text: root.label("Usuário", "Username"); color: "#dddcd5" }
                TextField {
                    id: user
                    enabled: !root.preview
                    Layout.fillWidth: true
                    text: userModel.lastUser
                    color: "#f0eade"; selectByMouse: true
                    background: Rectangle { color: "#272e30"; border.color: user.activeFocus ? "#c58f9d" : "#596161" }
                    onAccepted: password.forceActiveFocus()
                }
                Label { text: root.label("Senha", "Password"); color: "#dddcd5" }
                TextField {
                    id: password
                    enabled: !root.preview
                    Layout.fillWidth: true
                    echoMode: TextInput.Password
                    color: "#f0eade"
                    background: Rectangle { color: "#272e30"; border.color: password.activeFocus ? "#c58f9d" : "#596161" }
                    onAccepted: root.signIn()
                }
                ComboBox {
                    id: sessions
                    Layout.fillWidth: true
                    model: sessionModel
                    textRole: "name"
                    currentIndex: sessionModel.lastIndex
                    background: Rectangle { color: "#30383a"; border.color: "#596161" }
                    contentItem: Text { text: sessions.displayText; color: "#eee7dc"; verticalAlignment: Text.AlignVCenter; leftPadding: 10 }
                }
                Button {
                    id: loginButton
                    enabled: !root.preview
                    text: root.label("Entrar", "Sign in")
                    Layout.fillWidth: true
                    background: Rectangle { color: loginButton.down ? "#986b79" : "#c58f9d" }
                    contentItem: Text { text: loginButton.text; color: "#171c1c"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.bold: true }
                    onClicked: root.signIn()
                }
                Label { id: feedback; color: "#f3c6c1"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                RowLayout {
                    Layout.fillWidth: true
                    Button {
                        id: restartButton
                        text: root.label("Reiniciar", "Restart")
                        enabled: sddm.canReboot
                        onClicked: sddm.reboot()
                        background: Rectangle { color: "#30383a"; border.color: "#596161" }
                        contentItem: Text { text: restartButton.text; color: "#eee7dc"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                    }
                    Item { Layout.fillWidth: true }
                    Button {
                        id: powerButton
                        text: root.label("Desligar", "Shut down")
                        enabled: sddm.canPowerOff
                        onClicked: sddm.powerOff()
                        background: Rectangle { color: "#30383a"; border.color: "#596161" }
                        contentItem: Text { text: powerButton.text; color: "#eee7dc"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                    }
                }
                Label { text: "gorigamia · RoseShell · Debian"; color: "#aeb8af"; font.pixelSize: 11 }
            }
        }
    }
    Connections {
        target: sddm
        function onLoginFailed() {
            password.text = ""
            feedback.text = root.label("Não foi possível entrar. Confira usuário e senha.", "Could not sign in. Check username and password.")
            password.forceActiveFocus()
        }
        function onLoginSucceeded() { password.text = "" }
    }
    Component.onCompleted: { if (user.text.length > 0) password.forceActiveFocus(); else user.forceActiveFocus() }
}
