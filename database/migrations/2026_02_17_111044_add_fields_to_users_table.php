<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
   public function up()
{
  Schema::table('users', function (Blueprint $table) {
    $table->string('contact')->unique()->after('email');
    $table->text('biography')->nullable();
    $table->string('address')->nullable();
    $table->string('gender')->nullable();
    $table->string('image')->nullable();

    // Recommendation-related
    $table->string('preferred_style')->nullable();
    $table->string('preferred_color')->nullable();
    $table->string('body_type')->nullable();

    $table->string('role')->default('user');
});
}

};
