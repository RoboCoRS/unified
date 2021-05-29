#include <Arduino.h>
#include <ESPAsyncWebServer.h>
#include <WiFi.h>

#include "base64.h"
#include "base_html.h"

String image_new = "";
String image_old = "";

AsyncWebServer server(80);

void setup() {
    Serial.begin(350000);
    WiFi.softAP("STEIN", "123456789");

    server.on("/", HTTP_GET, [&](AsyncWebServerRequest *request) {
        request->send(200, "text/html", base_html);
    });
    server.on("/pic", HTTP_GET, [&](AsyncWebServerRequest *request) {
        request->send(200, "text/html", image_old);
    });
    server.on("/scenario", HTTP_GET, [&](AsyncWebServerRequest *request) {
        auto count = request->params();
        for (size_t i = 0; i < count; i++) {
            auto param = request->getParam(i);
            if (param->name() == "index") {
                auto value = param->value().toInt();
                Serial.write(value);
            }
        }
        request->redirect("/");
    });

    server.begin();
}

void loop() {
    if (Serial.available()) {
        image_new = Serial.readStringUntil('*');
        image_old = std::move(image_new);
    }
}
