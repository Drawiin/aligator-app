package com.drawiin.miseenplace

interface Platform {
    val name: String
}

expect fun getPlatform(): Platform